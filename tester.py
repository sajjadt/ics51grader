# Contact: sajjadt@uci.edu

import os
from subprocess import Popen, PIPE, TimeoutExpired
import re
from string import Template

# Load PRIVATE test 1 template
from test_templates.private_test1 import template
from test_templates.private_test1 import part1_grade
from test_templates.private_test1 import part2_grade

submissions_dir = "Submissions"
tester_template = Template(template)
VERBOSE = True
verbose_print = print if VERBOSE else lambda *a, **k: None

num_processed = 0
invalid_submission_format = []
bad_encoding = []
failed_parsing = []
timed_out = []
runtime_error = []
grades = {}

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

    student_name = student_id = part1 = part2 = None

    r = lines.find("student_name")
    s = lines.find(os.linesep, r)
    if r>=0 and s>=0:
        student_name = lines[r:s]

    r = lines.find("student_id")
    s = lines.find(os.linesep, r)
    if r >= 0 and s >= 0:
        student_id = lines[r:s]

    r = lines.find("Part 1: your code begins here")
    s = lines.find(os.linesep, r)
    start = s

    r = lines.find("Part 1: your code ends here")
    s = lines.rfind(os.linesep, 0, r)
    end = s

    if start >= 0 and end >= 0:
        part1 = lines[start:end]

    r = lines.find("Part 2: your code begins here")
    s = lines.find(os.linesep, r)
    start = s

    r = lines.find("Part 2: your code ends here")
    s = lines.rfind(os.linesep, 0, r)
    end = s
    if start >= 0 and end >= 0:
        part2 = lines[start:end]

    if not student_id or not student_name or not part1 or not part2:
        failed_parsing.append(file_name)
        continue

    code = tester_template.safe_substitute(student_name=student_name,
                                           student_id=student_id,
                                           part1=part1,
                                           part2=part2)
    # Create a temp file
    temp_file_name = "temp.s"
    file = open(os.path.join(submissions_dir, temp_file_name), 'w+')
    file.write(code)
    file.close()

    with Popen(['spim', '-file', os.path.join(submissions_dir, temp_file_name)], stdout=PIPE, stderr=PIPE) as p:
        try:
            output, errors = p.communicate(timeout=2)
            lines = output.decode('utf-8').splitlines()
            verbose_print(os.linesep.join(lines))

            name = lines[-4]
            id = lines[-3]
            part1_output = lines[-2].split()
            part2_output = lines[-1].split()

            grades[id] = (id, name, part1_grade(part1_output), part2_grade(part2_output))

        except TimeoutExpired as e:
            p.kill()
            timed_out.append(file_name)
        except Exception as e:
            p.kill()
            runtime_error.append(file_name)
        num_processed += 1


print("Processed {0} files".format(num_processed))
print("Invalid submission format:", invalid_submission_format)
print("Bad file encoding", bad_encoding)
print("Failed to parse", failed_parsing)
print("Timed out", timed_out)
print("Runtime error", timed_out)

for name, id, grade1, grade2 in grades.values():
    print(name, id, grade1, grade2)