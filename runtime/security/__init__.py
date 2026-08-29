from runtime.security.command_guard import CommandGuard

print(CommandGuard.validate("ipconfig"))
print(CommandGuard.validate("shutdown /s"))