from pathlib import Path
from time import sleep


class Class:
    """Stores information about an individual class"""

    def __init__(self, name):
        self.class_name = name
        self.class_path = ''
        self.students = []
        self.reset()
        self.number_of_students = self.count_students()
        self.work_found = 0
        self.all_found = False

    def set_path(self, path):
        self.class_path = Path(path)

    def add_student(self, student_name):
        self.students.append(Student(student_name))

    def add_unrecognised_file(self, file_name):
        """Keeps track of files that aren't associated with a student"""
        if file_name not in self.unrecognised_files:
            self.unrecognised_files.append(file_name)

    def reset_unrecognised_files(self):
        """Clears the list of unrecognised files. Used to stop multiple copies of the same file being in there.
        Could alternately make it check for existence, but this seems faster."""
        self.unrecognised_files = []

    def reset(self):
        """Resets read in file information. Stops a file being found, then vanishing and still showing as found."""
        self.reset_unrecognised_files()
        for student in self.students:
            student.reset_file_name()
        self.work_found = 0

    def count_found(self):
        for student in self.students:
            if student.file_found:
                self.work_found += 1

    def count_students(self):
        self.number_of_students = len(self.students)

    def check_if_finished(self):
        self.count_students()
        self.count_found()
        print(f'Found {self.work_found}/{self.number_of_students}')
        if self.work_found == self.number_of_students:
            self.all_found = True

    def __repr__(self):
        return f'Class {self.class_name}'


class Student:
    """Stores information about individual students"""

    def __init__(self, name):
        self.student_name = name
        self.file_found = False
        self.reset_file_name()

    def set_file_name(self, file_name):
        # Marks the student as found.
        self.file_name = f'<p id="found">{file_name}<p>'
        self.file_found = True

    def reset_file_name(self):
        # Default value is missing.
        self.file_name = '<p id="error">Missing<p>'
        self.file_found = False

    def __repr__(self):
        repr = f'Student: {self.student_name}, file: {self.file_name}'
        return repr


def read_classes():
    """Reads in class details from the associated file"""
    classes = []
    class_list_file = 'class_list.txt'

    with open(class_list_file) as f:
        # Set default values
        lines = f.readlines()
        class_name_set = False
        class_path_set = False
        # Keeps track of which class we are up to
        class_index = 0

        for line in lines:
            # Iterate through the lines of the file
            line = line.strip()  # To remove \n

            if line.startswith('Class'):
                if not class_name_set:
                    # A class can only have one name
                    try:
                        class_name = line.replace('Class ', '')
                        classes.append(Class(class_name))
                        class_name_set = True
                    except IndexError:
                        print(f'Class name not found: {line}.')
                        break
                else:
                    # If there is more than one Class line before an ENDCLASS is found.
                    raise ValueError('A class can not have multiple names. Previous class not terminated properly?')
            elif line.startswith('Path'):
                # Class name must be set first, and only one path can be set for a class.
                if class_name_set:
                    if not class_path_set:
                        try:
                            class_path = line.replace('Path ', '')
                            classes[class_index].set_path(class_path)
                            class_path_set = True
                        except IndexError:
                            print(f'Path found not specified: {line}.')
                            break
                    else:
                        # If there is more than one Path line before an ENDCLASS is found
                        raise ValueError('A class can not have multiple paths. Previous class not terminated properly?')
                else:
                    raise ValueError('Class name must be set before path is set.')
            elif line.startswith('END'):
                print(f'End of class {class_name} found.')
                class_index += 1
                class_name_set = False
                class_path_set = False
            else:
                if class_name_set and class_path_set:
                    # Only doable if the class has a name and path
                    student_name = line
                    classes[class_index].add_student(student_name)
                else:
                    raise ValueError('Class name and path must be set before students are added')
    return classes


def generate_html(individual_class):
    html = f'''<html>

    <head>
        <title> Class {individual_class.class_name}</title>
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

        <h3>{individual_class.work_found}/{individual_class.number_of_students} submitted</h3>
        <table>
            <tr>
                <th>Student name</th>
                <th>Submission status</th>
            </tr>'''

    for student in individual_class.students:
        html += f'''
        <tr>
            <th>{student.student_name}</th>
            <th>{student.file_name}</th>
        </tr>'''

    html += '</table>'

    if individual_class.unrecognised_files:
        # If there are unrecognised files, list them.
        html += '''
        <h2>Unrecognised files</h2>
        <ul>'''

        for unrecognised_file in individual_class.unrecognised_files:
            html += f'''<li id="error">{unrecognised_file}</li>'''
        html += '</ul>'

    with open('page.html', 'w') as f:
        # Turn that into HTML
        f.write(html)


def check_for_files(individual_class):
    """Checks the path to find all folders."""
    individual_class.reset()

    if individual_class.class_path.exists():
        # Read in all files in the path
        list_of_files = individual_class.class_path.glob('*.*')
        files = [x for x in list_of_files if x.is_file()]

        # Nested loop through files + students to add information about student.
        for file in files:
            file_name = file.parts[-1]
            for student in individual_class.students:
                student_name = student.student_name
                if student_name.lower() in file_name.lower():
                    if file.stat().st_size > 0:
                        print(f'Found "{file_name}" by {student_name}')
                        student.set_file_name(file_name)
                    else:
                        # If the file is empty
                        print(f'Found {file_name} but it is empty')
                        student.file_name = '<p id="error">Empty file - copy again<p>'
                    break
            else:
                print(f'No owner found for {file}')
                individual_class.add_unrecognised_file(file)
        individual_class.check_if_finished()
        print()
    else:
        raise ValueError(f'{individual_class.class_path} does not exist')


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

    while not chosen_class.all_found:
        # Check the folder for files
        check_for_files(chosen_class)

        # Generate an output
        generate_html(chosen_class)

        sleep(5)


main()
