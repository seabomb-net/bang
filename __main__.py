import sys
python_version = sys.version.split()[0]
if sys.version_info < (3, 10):
    print("""
                    .   .xXXXX+.   .
               .   ..   xXXXX+.-   ..   .   
         .   ..  ... ..xXXXX+. --.. ...  ..   .
     .   ..  ... .....xXXXX+.  -.-..... ...  ..   .
   .   ..  ... ......xXXXX+.  . .--...... ...  ..   . 
  .   ..  ... ......xXXXX+.    -.- -...... ...  ..   .
 .   ..  ... ......xXXXX+.   .-+-.-.-...... ...  ..   .
 .   ..  ... .....xXXXX+. . --xx+.-.--..... ...  ..   .
.   ..  ... .....xXXXX+. - .-xxxx+- .-- .... ...  ..   .
 .   ..  ... ...xXXXX+.  -.-xxxxxx+ .---... ...  ..   .
 .   ..  ... ..xXXXX+. .---..xxxxxx+-..--.. ...  ..   .
  .   ..  ... xXXXX+. . --....xxxxxx+  -.- ...  ..   .
   .   ..  ..xXXXX+. . .-......xxxxxx+-. --..  ..   .
     .   .. xXXXXXXXXXXXXXXXXXXXxxxxxx+. .-- ..   .
         . xXXXXXXXXXXXXXXXXXXXXXxxxxxx+.  -- .
           xxxxxxxxxxxxxxxxxxxxxxxxxxxxx+.--
            xxxxxxxxxxxxxxxxxxxxxxxxxxxxx+-\n""") # art by Ojosh!ro
    print(f"You are running Python {python_version}.".center(56))
    print(f"Please upgrade to 3.10 or newer to run BANG.".center(56))
    input("Enter any key to exit...".center(56))
    sys.exit(1)
import bang
bang.main()
    
