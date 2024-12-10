#!/usr/bin/env python
import sys
import warnings
from crew import Day7
from datetime import datetime

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run(input_params=None):
    """
    Run the crew.
    """
    inputs = {
        'topic': 'Moroccan Startups',
    }
    Day7().crew().kickoff(inputs=inputs)


run()