from pathlib import Path
from time import sleep


class Class:

    def __init__(self, name):
        self.class_name = name
        self.class_path = ''
        self.students = []
        self.reset()

    def set_path(self, path):
        self.class_path = Path(path)

    def add_student(self, student_name):
        self.students.append(Student(student_name))

    def add_unrecognised_file(self, file_name):
        if file_name not in self.unrecognised_files:
            self.unrecognised_files.append(file_name)

    def reset_unrecognised_files(self):
        self.unrecognised_files = []

    def reset(self):
        self.reset_unrecognised_files()
        for student in self.students:
            student.reset_file_name()

    def __repr__(self):
        return f'Class {self.class_name}'


class Student:

    def __init__(self, name):
        self.student_name = name
        self.found = False
        self.reset_file_name()

    def set_file_name(self, file_name):
        self.file_name = f'<p id="found">{file_name}<p>'
        self.found = True

    def reset_file_name(self):
        self.file_name = '<p id="error">Missing<p>'

    def __repr__(self):
        repr = f'Student: {self.student_name}, file: {self.file_name}'
        return repr


def read_classes():
    classes = []

    with open('class_list.txt') as f:
        lines = f.readlines()
        class_name_set = False
        class_path_set = False
        students = []
        class_index = 0
        for line in lines:

            line = line.strip()
            if line.startswith('Class') and not class_name_set:
                try:
                    class_name = line.replace('Class ', '')
                    classes.append(Class(class_name))
                    class_name_set = True
                except IndexError:
                    print(f'Class name not found: {line}.')
                    break
            elif line.startswith('Path') and not class_path_set:
                try:
                    class_path = line.replace('Path ', '')
                    classes[class_index].set_path(class_path)
                    class_path_set = True
                except IndexError:
                    print(f'Path found not specified: {line}.')
                    break
            elif line.startswith('END'):
                print(f'End of class {class_name} found.')
                class_index += 1

                class_name_set = False
                class_path_set = False
            else:
                student_name = line
                classes[class_index].add_student(student_name)
    return classes


def create_html(individual_class):
    html = f'''<html><head>
    <title> {individual_class.class_name}</title>
    <meta http-equiv="refresh" content="10">
    <style>
    #error {{
      color: red;
    }}
    #found {{
      color: green;
    }}
    </style>
    

    </head>
    <body>
    <h1>Submittor for {individual_class.class_name}</h1>
    <h2>Submit to {individual_class.class_path}</h2>
    <table>
    <tr>
    <th>Student name</th>
    <th>Submission status</th>
      </tr>    '''

    for student in individual_class.students:
        html += f'''<tr>
        <th>{student.student_name}</th>
        <th>{student.file_name}</th>
      </tr>'''

    html += '''</table>'''

    if individual_class.unrecognised_files:
        html += '''
        <h2>Unrecognised files</h2>
        <ul>'''

        for file in individual_class.unrecognised_files:
            html += f'''<li>{file}</li>'''
        html += '''</ul>'''

    with open('page.html', 'w') as f:
        f.write(html)

def check_for_files(individual_class):
    # Reset data each time it is checked. Marginaly more inefficient but fixes issue of data that was there vanishing and being shown as there.
    individual_class.reset()
    # Read in all files in the path
    if individual_class.class_path.exists():
        list_of_files = individual_class.class_path.glob('*.*')
        files = [x for x in list_of_files if x.is_file()]
        # Create a dict of statuses for each student
        for file in files:
            file_name = file.parts[-1]
            print(file)
            for student in individual_class.students:
                student_name = student.student_name
                if student_name in file_name:
                    size = file.stat().st_size
                    if size == 0:
                        print(f'Found {file_name} but empty')
                        student.file_name = '<p id="error">Empty file - copy again<p>'
                    else:
                        print(f'Found {student_name}')
                        student.set_file_name(file_name)
                    break
            else:
                individual_class.add_unrecognised_file(file)
    else:
        print('Path does not exist')
    a=123

def show_menu(classes):
    print('Please choose a class:')
    for number, individual_class in enumerate(classes, 1):
        print(f'{number}: {individual_class.class_name}')
    chosen_class = int(input('> '))
    class_index = chosen_class - 1
    return classes[class_index]


def main():
    # Read in class information
    classes = read_classes()

    # Present the menu so user chooses class
    chosen_class = show_menu(classes)

    while True:
        # Check the folder for files
        check_for_files(chosen_class)

        # Generate an output
        create_html(chosen_class)

        sleep(5)

main()