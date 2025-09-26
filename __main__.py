import sys
python_version = sys.version.split()[0]
if sys.version_info < (3, 10):
    print(f"BANG requires Python 3.10+\nYou are using Python {python_version}, which is not supported by BANG.")
    input("Enter any key to exit...")
    sys.exit(1)
import bang
bang.main()
    
