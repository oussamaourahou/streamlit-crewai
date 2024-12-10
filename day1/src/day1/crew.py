from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from dotenv import load_dotenv

load_dotenv()


@CrewBase
class Day1:
	"""Day1 crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	@agent
	def joke_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['joke_creator'],
			verbose=True
		)

	@agent
	def joke_judge(self) -> Agent:
		return Agent(
			config=self.agents_config['joke_judge'],
			verbose=True
		)

	@task
	def joke_task(self) -> Task:
		return Task(
			config=self.tasks_config['joke_task'],
		)

	@task
	def judge_task(self) -> Task:
		return Task(
			config=self.tasks_config['judge_task'],
			#output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Day1 crew"""
		return Crew(
			agents=self.agents, 
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
