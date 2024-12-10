#!/usr/bin/env python
import sys
import warnings

from crew import Day3
from datetime import datetime
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'Whatsapp Developers API and toolkil',
        'time': datetime.now().strftime('%Y-%m-%d')
    }
    Day3().crew().kickoff(inputs=inputs)

run()