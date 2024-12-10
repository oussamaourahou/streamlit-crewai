from datetime import datetime
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from tools.custom_tool import CustomSerperDevTool

@CrewBase
class Day7:
	"""Day7 crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	def __init__(self, input_params=None):
		self.input_params = input_params or {}
		self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

	
	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			tools=[CustomSerperDevTool(), ScrapeWebsiteTool()],
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
					)
	@task
	def reporting_task(self) -> Task:
		filename = f'report_{self.timestamp}.md'
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file=filename
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Day5 crew"""
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
		)
