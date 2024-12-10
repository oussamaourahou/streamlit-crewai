from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff


@CrewBase
class Day2:
	"""Day2 crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	ollama=LLM(model='ollama/llama3.2:3b',base_url='http://localhost:11434')


	@agent
	def Customer_query_generator(self) -> Agent:
		return Agent(
			config=self.agents_config['Customer_query_generator'],
			# tools=[MyCustomTool()], # Example of custom tool, loaded on the beginning of file
			verbose=True,
			LLM=self.ollama
		)

	@agent
	def query_escalation(self) -> Agent:
		return Agent(
			config=self.agents_config['query_escalation'],
			verbose=True,
			LLM=self.ollama
		)

	@task
	def generate_query(self) -> Task:
		return Task(
			config=self.tasks_config['generate_query'],
		)

	@task
	def escalate_query(self) -> Task:
		return Task(
			config=self.tasks_config['escalate_query'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Day2 crew"""
		return Crew(
			agents=self.agents, 
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
		)
