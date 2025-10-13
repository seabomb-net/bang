# to do: documentation
from ast import literal_eval as evaluate        # safe eval()
from configparser import ConfigParser as cfg    # config.ini
from datetime import datetime                   # file management
import os
from pathlib import Path                        # file management
from random import shuffle                      # shuffles pairs
import re
import shutil
import sys                                      # file management
from time import sleep as wait                  # exit
from time import time                           # timer

ROOT_DIR = Path('.').resolve() # working dir
SETS_DIR = Path('Sets').resolve() # study sets dir
INI_FILE = 'config.ini' # config file

class Disk:
    """Disk functions."""
    @staticmethod
    def boot(error=False) -> None:
        """Initialize INI_FILE and SETS_DIR if they do not exist."""
        if not os.path.exists(INI_FILE) or error:
            config = cfg()
            config['Options'] = {
                'reverse': 'False',
                'shuffle': 'True',
                'result': 'True',
                'saveq': 'False',
                'exact': 'False'
            }
            with open(INI_FILE, 'w') as file:
                config.write(file)

        if not os.path.exists(SETS_DIR):
            directory = ROOT_DIR / SETS_DIR
            directory.mkdir(parents=True, exist_ok=True)
                
    @staticmethod
    def load() -> None:
        """Load configuration from INI_FILE."""
        config = cfg()
        try:
            config.read(INI_FILE)
        except:
            Disk.boot(error=True)
        finally:
            Options.reverse = config.getboolean('Options', 'reverse', fallback=False)
            Options.shuffle = config.getboolean('Options', 'shuffle', fallback=True)
            Options.result = config.getboolean('Options', 'result', fallback=True)
            Options.saveq = config.getboolean('Options', 'saveq', fallback=False)
            

    @staticmethod
    def save() -> None: # save config
        """Save configuration to INI_FILE."""
        config = cfg()
        config['Options'] = {
            'reverse': str(Options.reverse),
            'shuffle': str(Options.shuffle),
            'result': str(Options.result),
            'saveq': str(Options.saveq)
        }
        with open(INI_FILE, 'w') as file:
            config.write(file)

    @staticmethod
    def duplicate(folder: str) -> None:
        """Duplicate a folder in SETS_DIR."""
        try:
            src = SETS_DIR / folder
            stem = f"{folder} (Copy)"
            dst = SETS_DIR / stem
            i = 1
            while dst.exists():
                i += 1;
                dst = SETS_DIR / f"{folder} (Copy {i})"
            shutil.copytree(src, dst)
        except (FileNotFoundError, FileExistsError) as e:
            print(f"An unexpected error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
class Write: # file-writing functions
    @staticmethod
    def set_create(title: str) -> str:
        """Initialize directory and text file; called only by Write.create()."""
        directory = SETS_DIR / title
        directory.mkdir(parents=True, exist_ok=True)
        txt = directory / "pairs.txt"
        with open(txt, 'a') as file:
            file.write(f"[{title} : Pairs]\n")
        return txt

    @staticmethod
    def score(scores: dict, folder: str) -> None: # initializes, saves and *overwrites* score dict as text
        """Initialize, save, and overwrite scores for flashcards."""
        directory = SETS_DIR / folder
        directory.mkdir(parents=True, exist_ok=True)
        txt = directory / "flashcards.txt"
        with open(txt, 'w') as file:
            file.write(f"[{folder} : Flashcards]\n")
            file.write(f'{scores}')
            
    @staticmethod
    def saveq(results: str, folder: str) -> None: # saves quiz results, creates a subfolder
        """Save quiz results and creates a new directory."""
        directory = SETS_DIR / folder / Path("Results")
        directory.mkdir(parents=True, exist_ok=True)
        qtime = datetime.now().strftime('%Y-%m-%d %H_%M_%S')
        txt = directory / f"{qtime}.txt"
        with open(txt, 'a') as file:
            file.write(f"[{folder}]\n")
            file.write(f'{results}')
        return txt

    @staticmethod
    def create(pairs:list=None, new=True, extract=False, folder=None) -> None:
        """Wizard to add terms and definitions to set; store pairs as tuples."""
        folders = [folder.name for folder in SETS_DIR.iterdir()]
        special = ['&', '"', '?', '<', '>', '#', '{', '}', '%', '~', '/', '.', # me
                   '\\', '*', ';', ':', "'", '|', '\t', '\n', '$', '!', '[', ']']
        if new:
            while True:
                title = input('\nTitle your set: ').strip()
                if title == 'x':
                    print('Returning...')
                    return
                elif any(char in special for char in title) or title.lower() == 'flashcards':
                    print('Invalid title, try again...')
                    continue
                elif title in folders: # duplicate checker
                    print(f"'{title}' already exists, try again...")
                    continue
                elif title:
                    break
                else:
                    print('Invalid title, try again...')
                    continue
            txt = Write.set_create(title) ##
        else:
            txt = SETS_DIR / folder / "pairs.txt"
        if extract:
            return txt, title
        terms = []
        if pairs:
            for term, definition in pairs:
                terms.append(term)
        while True:
            while True:
                term = input("\nEnter a term, or enter 'x' to finish: ").strip()
                if terms and term.lower() == 'x' and new:
                    print(f"Set '{title}' successfully created!")
                    del terms
                    return
                elif terms and term.lower() == 'x':
                    print(f"Pair(s) successfully added!")
                    del terms
                    return
                elif not terms and term.lower() == 'x':
                    print('Returning...')
                    if new: Write.dir_delete(title, user=False)
                    return
                elif term in terms:
                    print(f"'{term}' already exists, try again...")
                    continue
                elif term == 's' or term == 'self':
                    print('Invalid term, try again...')
                elif term: break
                else:
                    print('Invalid term, try again...')
                    continue
            while True:
                definition = input('Enter a definition: ').strip()
                if terms and definition.lower() == 'x':
                    if new: print(f"Set '{title}' successfully created!")
                    del terms
                    return
                elif not terms and definition.lower() == 'x':
                    print('Returning... ')
                    Write.dir_delete(title, user=False, reset=False)
                    del terms
                    return
                elif term == 's' or term == 'self':
                    print('Invalid term, try again...') 
                elif definition: break
                else:
                    print('Invalid definition, try again...')
                    continue
            pair: tuple = (term, definition)
            with open(txt, 'a') as file:
                file.write(f"{pair}\n")
                terms.append(term)
                print("Added!")
                continue

    @staticmethod
    def extract(txt, title) -> list:
        """Separate user input into a list; only for use with importing."""
        while True:
            inner: str = input('Enter a character to separate between term and definition, or leave blank to use double percent (%%): ').strip()
            if not inner:
                inner = '%%'
            elif inner.lower() == 'x':
                Write.dir_delete(title, user=False)
                print('Returning...')
                return
            outer: str = input('Enter a character to separate between pairs, or leave blank to use double star (**): ').strip()
            if not outer:
                outer = '**'
            elif outer.lower() == 'x':
                Write.dir_delete(title, user=False)
                print('Returning...')
                return
            extraction: str = str(input('Enter output to import: ')).split(outer)
            pairs = []
            try:
                for pair in extraction:
                    if pair:
                        term, definition = pair.split(inner)
                        pairs.append((term, definition))
                return pairs
            except ValueError:
                print('Invalid entry, try again...\n')
                continue
    
    @staticmethod
    def strip(pairs: list, txt: str | None, title: str) -> bool:
        """Sanitize pairs from extract() into tuples; only for use with importing."""
        for idx, pair in enumerate(pairs, start=1):
            print(f"{idx}. {str(pair)[:75]}{'...' if len(str(pair)) > 75 else ''}")
        while True:
            selection = input(f'Looks good? (y/n): ').strip().lower()
            if selection == 'y':
                with open(txt, 'a') as file:
                    for pair in pairs:
                        file.write(f"{pair}\n")
                print(f"Set '{title}' successfully created!")
                return True
            elif selection == 'n' or selection == 'x':
                del pairs
                print()
                return False
            else:
                print('Invalid selection, try again...')
                continue
        
    @staticmethod
    def dir_delete(folder: str, user=True, reset=False) -> bool | None: # user and reset args are for UI
        """Delete a directory or clear everything."""
        if user:
            message = f"Delete '{folder}'? (y/n): " if not reset else \
                      f"Clear all data? This cannot be undone. (y/n): "
            while True:
                selection = input(message).strip().lower()
                if selection == 'y': break
                elif selection == 'n' or selection == 'x':
                    print('Returning...')
                    return
                else:
                    print('Invalid selection, try again...')
                    continue
        target = SETS_DIR / folder
        try:
            shutil.rmtree(target)
            if reset: input('Reset complete. Enter any key to continue... ')
            return True
        except Exception as e:
            if user: print(f"An unexpected error occurred: {e}")
            return False

    @staticmethod
    def delete(file: str) -> None:
        """Delete one individual file."""
        try:
            os.remove(file)
        except FileNotFoundError:
            pass
        
    @staticmethod
    def edit(pair: tuple, pairs: list, folder: str) -> list:
        """Wizard to edit individual pairs within a set."""
        flashcards = SETS_DIR / folder / 'flashcards.txt'
        blank = False
        swap = False
        terms = []
        for term, definition in pairs:
            terms.append(term)
        print("Enter new item, 's' to swap pair, or press Enter to keep current...")
        while True:
            new_term = input(f"Term: {pair[0]}: ").strip()
            if new_term.lower() == 'x':
                print('Returning...')
                return pairs
            elif new_term.lower() == 's':
                swap = True
                break
            elif not new_term:
                new_term = pair[0]
                break
            elif any(new_term in terms for term in terms):
                print(f"'{new_term}' already exists, try again...")
                continue
            else: break
        while True and not swap:
            new_def = input(f'Definition: {pair[1]}: ').strip()
            if new_def.lower() == 'x':
                print('Returning...')
                return pairs
            elif new_def.lower() == 's':
                print('Invalid term, try again...')
                continue
            elif not new_def:
                new_def = pair[1]
                break
            elif new_def:
                break
                print('Invalid term, try again...')
                continue
        if swap:
            new_term = pair[1]
            new_def = pair[0]
        if new_term == pair[0] and new_def == pair[1]:
            blank = True
        if not blank:
            Write.delete(flashcards)
        txt = SETS_DIR / folder / "pairs.txt"
        for i, (term, definition) in enumerate(pairs):
            if term == pair[0] and definition == pair[1]:
                del pairs[i]
                break
        new_pair = (new_term, new_def)
        pairs.append(new_pair)
        txt = SETS_DIR / folder / "pairs.txt"
        if not blank:
            pass ### Write code that uses an import of shutil that deletes a FILE, not a DIRECTORY.
        with open(txt, 'w') as file:
            file.write(f"[{folder} : Pairs]\n")
            for term, definition in pairs:
                file.write(f"{(term, definition)}\n")
        print(f"{'No changes were saved.' if blank else 'Edited pair!'}")
        return pairs

class Read: # file-reading functions
    @staticmethod
    def correct(data: str, answer: str) -> bool:
        data = data.lower() # user input
        answer = answer.lower()
        parentheses = answer.split('(')[1].split(')')[0] if "(" in answer and ")" in answer and not Options.exact else None
        ### ^^^ if there are parentheses in the answer i.e. "water (liquid)", "liquid" is an acceptable input
        not_parentheses = answer.split('(')[0].strip() if parentheses and not Options.exact else None
        ### ^^^ "water" is also an acceptable input
        if data in answer and len(data) >= (len(answer)*.9):
            return True
        elif parentheses:
            if data in parentheses and len(data) >= (len(parentheses)*.9):
                return True
            elif data in not_parentheses and len(data) >= (len(not_parentheses)*.9):
                return True
        return False
    
    @staticmethod
    def edit(pairs: list, folder: str) -> tuple | str | None:
        """Select an individual pair within a set."""
        directory = SETS_DIR / folder
        txt = directory / "pairs.txt"
        flashcards = directory / "flashcards.txt"
        if not pairs:
            while True:
                selection = input(f'No pairs found. Delete set? (y/n): ').strip().lower()
                if selection == 'y':
                    del pairs
                    Write.dir_delete(folder, user=False)
                    print(f"Set '{folder}' was deleted.")
                    return
                elif selection == 'n' or selection == 'x':
                    del pairs
                    print(f'The set is accessible inside the Sets/{folder}/ directory.')
                    return
                else:
                    print('Invalid selection, try again...')
                    continue
            return None
        
    
        pairs = sorted(pairs)
        print(f"\nSelect pair #, *# to duplicate pair, or -# to delete pair, or 'c' to create pair: ")
        print("#")
        for idx, pair in enumerate(pairs, start=1):
            print(f"{idx}. {str(pair)[:75]}{'...' if len(str(pair)) > 75 else ''}")
        while True:
            pair=None
            control=True
            selection = input('').strip().lower()
            if selection == 'x':
                control=False
                print('Returning...')
                return pair, control
            elif selection == 'c':
                Write.delete(flashcards)
                return folder, control

            ######## PAIR DUPLICATION
            ######## GOAL: RECURSION
            elif selection.startswith('*'):##### in progress
                selection = selection.replace('*', '')
                try:
                    selection = int(selection)
                except ValueError:
                    print("Invalid selection, try again...")
                    continue
                if 1 <= selection <= len(pairs):
                    pair = pairs[selection-1]
                    pairs.append(pair)
                    with open(txt, 'a') as file:
                        file.write(f"{pair}\n")
                        pair=None
                        return pair, control
                else:
                    print("Invalid selection, try again...")
                    continue
            else:
                try:
                    selection = int(selection)
                    if 1 <= selection <= len(pairs): ## Typical set select
                        return pairs[selection - 1], control
                    elif -len(pairs) <= selection <= -1:
                        del pairs[abs(selection) - 1]
                        Write.delete(flashcards)
                        with open(txt, 'w') as file:
                            file.write(f"[{folder} : Pairs]\n")
                            for pair in pairs:
                                file.write(f"{pair}\n")
                        pair=None
                        return pair, control
                    else:
                        print('Invalid selection, try again...\n')
                        wait(1)
                        continue
                except ValueError:
                    print('Invalid selection, try again...\n')
                    wait(1)
                    continue
        
    @staticmethod
    def quiz(pairs: list, folder: str) -> None:
        """Display pairs from selected set in a quiz format."""
        if len(pairs) == 0:
            while True:
                selection = input(f'{folder} was unreadable. Delete set? (y/n): ').strip().lower()
                if selection == 'y':
                    del pairs
                    Write.dir_delete(folder, user=False)
                    print(f'{folder} was deleted. Returning...')
                    return
                elif selection == 'n' or selection == 'x':
                    del pairs
                    print(f'The file is accessible inside the Sets/{folder}/ directory.')
                    return
                else:
                    print('Invalid selection, try again...')
                    continue
        selection = 'r'
        while selection == 'r':
            questions_correct = 0
            skipped = 0
            t0 = time()
            for pair in pairs:
                while True:
                    selection = input(f'\n{pair[0]}: ').strip()
                    selection = selection.replace('self', f'{pair[0]}').lower()
                    control = Read.correct(selection, pair[1])
                    if selection == 'x':
                        print('Returning...')
                        return
                    elif selection == 's':
                        skipped += 1
                        break
                    elif control:
                        print(f'√ {pair[1]}')
                        questions_correct += 1
                        break
                    else:
                        print(f"✗ {pair[1] if Options.result else ''}")
                        correction = input("Enter any key to continue, or enter 'y' to override... ").strip().lower()
                        if correction == 'y':
                            if Options.result: print('√')
                            questions_correct += 1
                            break
                        elif correction == 'x':
                            print('Returning...')
                            return
                        break
            t1 = time()
            elapsed = Read.time_format(round(t1-t0, 0))
            print('\nQuiz complete!')
            results = (
                f'Results:'
                f'\nCorrect: {questions_correct}'
                f'\nIncorrect: {len(pairs)-questions_correct}'
                f'\nSkipped: {skipped}'
                f'\nTime elapsed: {elapsed}'
                f'\nYour grade: {round((questions_correct/len(pairs)*100), 2)}%')
            if Options.result:
                print()
                print(results)
            if Options.saveq:
                txt = Write.saveq(results, folder)
                print(f'Results have been saved to the Sets/{folder}/ directory.')
            selection = input("Enter any key to continue, or enter 'r' to retry... ").strip().lower()
            if selection == 'r':
                if Options.shuffle: shuffle(pairs)
                continue
            else:
                print('Returning...')
                return

    @staticmethod
    def time_format(seconds) -> str:
        """Format time into a readable string."""
        minutes = int((seconds % 3600) // 60)
        remainder = int(seconds % 60)
        hours = int(seconds // 3600)
        if hours:
            return f'{hours}h {minutes}m {remainder}s'
        elif minutes:
            return f'{minutes}m {remainder}s'
        else:
            return f'{seconds}s'

    @staticmethod
    def flashcards(pairs: list, folder: str) -> None: # not a quiz, the user personally assesses themselves
        """Display pairs from a selected set; assess user knowledge 1-5."""
        """The user personally grades themselves."""
        if len(pairs) == 0:
            while True:
                selection = input(f'{folder} was unreadable. Delete set? (y/n): ').strip().lower()
                if selection == 'y':
                    del pairs
                    Write.dir_delete(folder, user=False)
                    print(f'{folder} was deleted. Returning...')
                    return
                elif selection == 'n' or selection == 'x':
                    del pairs
                    print(f'The file is accessible inside the Sets/{folder}/ directory.')
                    return
                else:
                    print('Invalid selection, try again...')
                    continue
        selection = 'r'
        while selection == 'r':
            scores: dict = {} # initalizes every selection
            for pair in pairs:
                question_score = 0 # persistent
                while True:
                    selection = input(f"\n{'Definition' if Options.reverse else 'Term'}: {pair[0]} ")
                    if selection == 'x':
                        print('Returning...')
                        return
                    elif selection == 's': break
                    else:
                        print(f"{'Term' if Options.reverse else 'Definition'}: {pair[1]} ")
                    while True:
                        selection = input("How well did you know this (1-5)? ").strip().lower()
                        if selection == 'x':
                            print('Returning...')
                            return
                        try:
                            selection = int(selection)
                            if 1 <= selection <= 5: break
                            else:
                                print('Invalid input, try again...')
                                continue
                        except ValueError:
                            print('Invalid input, try again...')
                            continue
                        break
                    break
                try:
                    scores[pair] = selection # appends dict
                except UnboundLocalError:
                    scores[pair] = 1
            Write.score(scores, folder) # write only if the flashcards were complete
            del pairs
            print()
            nums = list(scores.values())
            if all(value == 5 for value in nums):
                print('Set Mastered!')
            print('Completed! Your personal assessment has been saved.')
            selection = input("Enter any key to continue, or enter 'r' to retry... ").strip().lower()
            if selection == 'r':
                pairs, folder = Read.order(folder) # evaluate the new order after file has been written
                Read.flashcards(pairs, folder) # recursive with purpose
                break
            else: break
    
    @staticmethod
    def parse(folder: str) -> tuple[list, str]:
        """From pairs.txt, evaluate and shuffle pairs."""
        pairs: list = []
        try:
            directory = SETS_DIR / folder
        except TypeError: # NoneType
            return
        txt = directory / "pairs.txt"
        try:
            with open(txt) as file:
                lines = file.readlines()[1:]
                if Options.shuffle: shuffle(lines)
                try:
                    for line in lines:
                        line = line.strip()
                        if not line: continue
                        pair = evaluate(line)
                        if Options.reverse:
                            pair = tuple(reversed(pair))
                        pairs.append(pair)
                except (ValueError, SyntaxError): pass
        except FileNotFoundError:
            while True:
                selection = input(f'{folder} was corrupted. Delete set? (y/n): ').strip().lower()
                if selection == 'y':
                    del pairs
                    Write.dir_delete(folder, user=False)
                    return
                elif selection == 'n' or selection == 'x':
                    del pairs
                    print(f'The corrupted file is accessible inside the Sets/{folder}/ directory.')
                    return
                else:
                    print('Invalid selection, try again...')
                    continue
        except Exception as e: print(f"An unexpected error occurred: {e}")
        return pairs, folder

    @staticmethod
    def order(folder: str) -> list: # evaluates dict, returns the list by self-assessment *lowest first*
        """From flashcards.txt, evaluate and shuffle pairs."""
        pairs = []
        try:
            directory = SETS_DIR / folder
        except TypeError:
            return
        txt = directory / "flashcards.txt"
        with open(txt) as file:
            next(file) # skips line 1
            keys = file.read()
        keys = evaluate(keys)
        pairs = sorted(keys, key=keys.get, reverse=False)
        return pairs, folder
    
    @staticmethod
    def view() -> str:
        """List directories in SETS_DIR."""
        folders = [folder.name for folder in SETS_DIR.iterdir()]
        if not SETS_DIR.exists():
            Read.zero()
            return
        if not folders:
            Read.zero()
            return
        while True:
            #control=False
            folders = sorted(folders)
            if folders:
                print("\nSelect set #, *# to duplicate set, -# to delete set, or 'c' to create set: ")
                print("#")
                for idx, sets in enumerate(folders, start=1):
                    print(f"{idx} * {sets}")
                while True:
                    selection = input('').strip().lower()
                    if selection == 'x':
                        print('Returning...')
                        return
                    elif selection == 'c':
                        Write.create()
                        return
                    elif selection.startswith('*'):
                        selection = selection.replace('*', '')
                        try:
                            selection = int(selection)
                        except ValueError:
                            print('Invalid selection, try again...')
                            continue
                        if 1 <= selection <= len(folders):
                            Disk.duplicate(folders[selection - 1])
                            folders = [folder.name for folder in SETS_DIR.iterdir()]
                            break
                        
                    else:
                        try:
                            selection = int(selection)
                            if 1 <= selection <= len(folders):
                                return folders[selection - 1] # the literal name of the txt
                            elif -len(folders) <= selection <= -1:
                                Write.dir_delete(folders[abs(selection) - 1], user=True)
                                folders = [folder.name for folder in SETS_DIR.iterdir()]
                                break
                            else:
                                print('Invalid selection, try again...')
                                continue
                        except ValueError:
                            print('Invalid selection, try again...')
                            continue
            else:
                Read.zero()
                return

    @staticmethod     
    def zero() -> None:
        """Handle edge cases for folder iteration errors."""
        while True:
            selection = input("\nNo sets found. Create a set? (y/n): ").strip().lower()
            if selection == 'y':
                Write.create()
                return
            elif selection == 'n' or selection == 'x':
                print('Returning...')
                return
            else:
                print('Invalid selection, try again...')
                continue

class Options:
    """Settings/Customization"""
    reverse = None # reverses pair order
    result = None # displays quiz results
    saveq = None # saves quiz results (txt)
    shuffle = None # shuffles pairs
    exact = None # exact answers only
                        
    @staticmethod
    def menu() -> None:
        """Display main settings."""
        Disk.load()
        while True:
            while True:
                print()
                print(f'Enter text in parentheses to modify: \n'
                      f"Reverse Pair Order = {'ON ' if Options.reverse else 'OFF'}       (--v)\n"
                      f"Quiz Settings...               (--q)\n"
                      f"Restore Defaults...            (--r)\n"
                      f"Hard Reset...                  (--h)")
                selection = input().strip().lower()
                match selection:
                    case '--v':
                        Options.reverse = not Options.reverse
                        Disk.save()
                    case '--q':
                        Options.quiz()
                    case '--r':
                        Options.reverse = False
                        Options.shuffle = True
                        Options.result = True
                        Options.saveq = False
                        Options.exact = False
                        Disk.save()
                        break
                    case '--h':
                        folders = [x for x in SETS_DIR.iterdir()]
                        if folders:
                            Write.dir_delete('.', user=True, reset=True)
                        else:
                            print('No sets to clear.')
                            continue
                        print()
                        main()
                        break
                    case 'x':
                        print('Returning...')
                        return
                    case _:
                        print("Invalid selection, try again...")
                        continue

    @staticmethod
    def quiz() -> None:
        """Display quiz-specific tweaks."""
        while True:
            while True:
                print()
                print(f'Enter text in parentheses to modify: \n'
                      f"Save Results = {'ON ' if Options.saveq else 'OFF'}             (--s)\n"
                      f"Show Results = {'ON ' if Options.result else 'OFF'}             (--q)\n"
                      f"Shuffle Pairs = {'ON ' if Options.shuffle else 'OFF'}            (--f)\n"
                      f"Exact Answers Only = {'ON ' if Options.exact else 'OFF'}       (--e)")
                selection = input().strip().lower()
                match selection:
                    case '--s':
                        Options.saveq = not Options.saveq
                        Disk.save()
                        break
                    case '--q':
                        Options.result = not Options.result
                        Disk.save()
                        break
                    case '--f':
                        Options.shuffle = not Options.shuffle
                        Disk.save()
                        break
                    case '--e':
                        Options.exact = not Options.exact
                        Disk.save()
                        break
                    case 'x':
                        print('Returning...')
                        return
                    case _:
                        print("Invalid selection, try again...")
                        continue
    @staticmethod
    def readme() -> None:
        with open("license.txt", "r") as file:
            print()
            print(file.read())
            input("Enter any key to return... ")

def welcome() -> None:
    """ASCII art from https://patorjk.com/software/taag/."""
    print(r"""██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗
██╔══██╗██╔══██╗████╗  ██║██╔════╝ ██║
██████╔╝███████║██╔██╗ ██║██║  ███╗██║
██╔══██╗██╔══██║██║╚██╗██║██║   ██║╚═╝
██████╔╝██║  ██║██║ ╚████║╚██████╔╝██╗
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝""")
    print("[*] seabomb.net\t       [*] 10.10.2025")

def menu() -> None:
    """Display menu."""
    while True:
        while True:
            print()
            print(f"Enter '--c' to create a set\n"
                  f"Enter '--e' to edit a set\n"
                  f"Enter '--f' to view flashcards\n"
                  f"Enter '--i' to import a set\n"
                  f"Enter '--q' to start quiz\n"
                  f"Enter '--o' to view options\n"
                  f"Enter '--x' to exit\n"
                  f"Enter '--z' to view credits\n"
                  f"(Input 'x' in any menu to go back)")
            selection = input().strip().lower()
            match selection:
                case '--c':
                    Write.create()
                    break
                case '--e':
                    #raise NotImplementedError
                    folder = Read.view()
                    control = True
                    while control:####
                        try:
                            pairs, folder = Read.parse(folder)
                        except TypeError:
                            break
                        pair, control = Read.edit(pairs, folder)
                        if not pair:
                            continue
                        if isinstance(pair, tuple):
                            print("if isinstance(pair, tuple):")
                            pairs = Write.edit(pair, pairs, folder)
                            continue
                        elif isinstance(pair, str):
                            Write.create(pairs, new=False, folder=folder)
                            pairs, folder = Read.parse(folder)
                            continue
                        else:
                            break
                case '--f':
                    # Control flow:
                    # parse(folder) evaluates folder.txt and returns a shuffled list;
                    # order(folder) evaluates flashcards.txt returns an ordered list;
                    # order() will only run if flashcards.txt exists, else parse()
                    folder = Read.view()
                    try:
                        pairs, folder = Read.order(folder)
                    except (SyntaxError, FileNotFoundError):
                        pairs, folder = Read.parse(folder)
                    except TypeError:
                        break
                    Read.flashcards(pairs, folder)
                    break
                case '--i':
                    try:
                        txt, title = Write.create(new=True, extract=True)
                    except TypeError:
                        break
                    while True:
                        pairs = Write.extract(txt, title)
                        try:
                            control = Write.strip(pairs, txt, title)
                        except TypeError:
                            break
                        if control: break
                        else: continue
                case '--q':
                    folder = Read.view()
                    try:
                        pairs, folder = Read.parse(folder)
                    except TypeError:
                        break
                    Read.quiz(pairs, folder)
                    break
                case '--o':
                    Options.menu()
                    break
                case '--x' | 'x':
                    print('Exiting...')
                    wait(1)
                    sys.exit()
                case '--z':
                    Options.readme()
                    break
                case _:
                    print("Invalid selection, try again...")
                    continue

def main() -> None:
    Disk.boot(error=False)
    Disk.load()
    welcome()
    menu()

if __name__ == '__main__': main()
