from nexa.commands.django.generate import handle as generate_handler

def handle(args):
    """
    Sync command is currently an alias for generate, 
    but provides a more 'dev-friendly' semantic for updating existing projects.
    """
    print("[*] Nexa Sync: Synchronizing project artifacts with schema...")
    generate_handler(args)
