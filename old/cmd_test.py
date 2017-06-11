#!/usr/bin/python

import cmd
import pprint

class HelloWorld(cmd.Cmd):
    """Simple command processor example."""
    
    FRIENDS = [ 'Alice', 'Adam', 'Barbara', 'Bob' ]
    prompt = "HQ>"
   
    def do_hello(self,stuff):
	"Say Hello World!"
	HellWorld.print_it()
 
    def do_greet(self, person):
        "Greet the person"
        if person and person in self.FRIENDS:
            greeting = 'hi, %s!' % person
        elif person:
            greeting = "hello, " + person
        else:
            greeting = 'hello'
        print greeting
    
    def complete_greet(self, text, line, begidx, endidx):
        if not text:
            completions = self.FRIENDS[:]
        else:
            completions = [ f
                            for f in self.FRIENDS
                            if f.startswith(text)
                            ]
        return completions

    def help_help(this):
	print "help help help"

    def do_EOF(self, line):
	"Exit the Game"
        return True

if __name__ == '__main__':
    HelloWorld().cmdloop()
