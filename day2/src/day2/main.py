#!/usr/bin/env python
import sys
import warnings
from crew import Day2

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    day2 = Day2()
    crew = day2.crew()
    return crew.kickoff()

if __name__ == "__main__":
    run()
