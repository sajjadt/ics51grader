# Contact: sajjadt@uci.edu

import os
from subprocess import Popen, PIPE
import re
from string import Template

# Load public test 1 template
from test_templates.public_test1 import template

submissions_dir = "Submissions"
tester_template = Template(template)
VERBOSE = True
verbose_print = print if VERBOSE else lambda *a, **k: None

num_processed = 0
invalid_submission_format = []
bad_encoding = []
failed_parsing = []

failed_on_part1 = []
failed_on_part2 = []

# matches {file_name}.s
submission_pattern = re.compile(r"(.*)\.s")



for file_name in os.listdir(submissions_dir):
    verbose_print("Processing", file_name)

    # Skip OS backup files
    if file_name.startswith(".") or file_name.startswith("~"):
        continue

    # Skip invalid submission
    if not submission_pattern.match(file_name):
        invalid_submission_format.append(file_name)
        continue

    lines = []
    try:
        with open(os.path.join(submissions_dir, file_name), 'r') as file:
            lines = file.read()
    except Exception as e:
        # Skip bad encoding
        bad_encoding.append(file_name)
        continue

    r = lines.find("student_name")
    s = lines.find(os.linesep, r)
    student_name = lines[r:s]

    r = lines.find("student_id")
    s = lines.find(os.linesep, r)
    student_id = lines[r:s]

    r = lines.find("Part 1: your code begins here")
    s = lines.find(os.linesep, r)
    start = s

    r = lines.find("Part 1: your code ends here")
    s = lines.rfind(os.linesep, 0, r)
    end = s

    part1 = lines[start:end]

    r = lines.find("Part 2: your code begins here")
    s = lines.find(os.linesep, r)
    start = s

    r = lines.find("Part 2: your code ends here")
    s = lines.rfind(os.linesep, 0, r)
    end = s
    part2 = lines[start:end]

    if not student_id or not student_name: #  or not part1 or not part2:
        failed_parsing.append(file_name)
        continue

    code = tester_template.safe_substitute(student_name = student_name,
                                      student_id = student_id,
                                      part1 = part1,
                                      part2 = part2)
    # Create a temp file
    temp_file_name = "~temp.s"
    file = open(os.path.join(submissions_dir, temp_file_name), 'w+')
    file.write(code)
    file.close()

    with Popen(['spim', '-file', os.path.join(submissions_dir, temp_file_name)], stdout=PIPE, stderr=PIPE) as p:
        output, errors = p.communicate()
        lines = output.decode('utf-8').splitlines()
        verbose_print(os.linesep.join(lines))
        num_processed += 1

print("Processed {0} files".format(num_processed))
print("Invalid submission format:" , invalid_submission_format)
print("Bad encoding", bad_encoding)
print("Failed to parse", failed_parsing)
