import asyncio

import structlog
from agents import (
  Agent,
  GuardrailFunctionOutput,
  InputGuardrail,
  Model,
  ModelProvider,
  OpenAIResponsesModel,
  RunConfig,
  RunContextWrapper,
  Runner,
  TResponseInputItem,
)
from agents.exceptions import InputGuardrailTripwireTriggered
from openai import AsyncOpenAI
from pydantic import BaseModel

from utils.settings import configure_logging, settings

# Configure logging early
configure_logging(settings.log_level)
log = structlog.get_logger(__name__)


class DefaultModelProvider(ModelProvider):
  """A model provider that returns a default model instance."""

  _default_model_instance: Model

  def __init__(self, model_name: str, client: AsyncOpenAI):
    self._default_model_instance = OpenAIResponsesModel(
      model=model_name, openai_client=client
    )

  def get_model(self, model_name: str | None = None) -> Model:
    """Return the default model, ignoring any specific model name."""
    return self._default_model_instance


class HomeworkOutput(BaseModel):
  is_homework: bool
  reasoning: str


guardrail_agent = Agent(
  name='Guardrail check',
  instructions='Check if the user is asking about homework.',
  output_type=HomeworkOutput,
)

math_tutor_agent = Agent(
  name='Math Tutor',
  handoff_description='Specialist agent for math questions',
  instructions='You provide help with math problems. Explain your reasoning at each step and include examples',
)

history_tutor_agent = Agent(
  name='History Tutor',
  handoff_description='Specialist agent for historical questions',
  instructions='You provide assistance with historical queries. Explain important events and context clearly.',
)


async def homework_guardrail(
  ctx: RunContextWrapper, agent: Agent, input_data: str | list[TResponseInputItem]
):
  # For simplicity, this guardrail only handles string inputs
  if not isinstance(input_data, str):
    return GuardrailFunctionOutput(output_info=None, tripwire_triggered=False)

  log.debug('Running homework guardrail...', input_data=input_data)
  result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
  final_output = result.final_output_as(HomeworkOutput)

  log.debug(
    'Guardrail check result',
    is_homework=final_output.is_homework,
    tripwire_triggered=not final_output.is_homework,
  )

  return GuardrailFunctionOutput(
    output_info=final_output,
    tripwire_triggered=not final_output.is_homework,
  )


triage_agent = Agent(
  name='Triage Agent',
  instructions="You determine which agent to use based on the user's homework question",
  handoffs=[history_tutor_agent, math_tutor_agent],
  input_guardrails=[
    InputGuardrail(guardrail_function=homework_guardrail),
  ],
)


async def main():
  log.info(
    'Starting agent run',
    model=settings.default_model,
    log_level=settings.log_level,
  )

  client = AsyncOpenAI(api_key=settings.openai_api_key)
  model_provider = DefaultModelProvider(
    model_name=settings.default_model, client=client
  )
  run_config = RunConfig(model_provider=model_provider)

  # Example 1: History question
  try:
    log.info('Running agent for history question...')
    result = await Runner.run(
      triage_agent,
      'who was the first president of the united states?',
      run_config=run_config,
    )
    log.info('Agent finished', final_output=result.final_output)
  except InputGuardrailTripwireTriggered as e:
    log.warning('Guardrail blocked input', reason=str(e))

  # Example 2: General/philosophical question
  try:
    log.info('Running agent for philosophical question...')
    result = await Runner.run(
      triage_agent, 'What is the meaning of life?', run_config=run_config
    )
    log.info('Agent finished', final_output=result.final_output)
  except InputGuardrailTripwireTriggered as e:
    log.warning('Guardrail blocked input', reason=str(e))


if __name__ == '__main__':
  asyncio.run(main())
