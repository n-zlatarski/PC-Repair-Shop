"""Symptoms visible to customers; underlying causes remain in the job model."""
# First four tickets preserve the existing workshop's order. The following six
# teach inspection, connection checks, requirements and avoiding needless parts.
REQUESTS={
 'RAM fault':('Unexpected restarts',150,'It freezes or restarts while I have several things open. I do not know which part is causing it. Can you find out?'),
 'RAM upgrade':('More memory, please',160,'I have 8 GB RAM. Please upgrade to at least 16 GB of compatible memory.'),
 'Storage fault':('Files will not open',190,'It takes ages to start and sometimes a file will not open. I have a backup of everything. Could you check the computer?'),
 'GPU fault':('Strange squares on screen',300,'Games show coloured squares and then close. My friend says it might be the memory, but I am not sure.'),
 'Storage cable':('No boot device',100,'After I moved house it stopped starting. The screen says there is no boot device. It worked before the move.'),
 'GPU cable':('Fans spin, screen stays black',110,'I cleaned inside it yesterday. Now the fans spin but my monitor stays black. Have I broken something?'),
 'RAM seating':('No start after cleaning',100,'I took some dust out. It switches on but never gets to the desktop. I may have bumped something inside.'),
 'Storage power':('Drive has disappeared',100,'My files disappeared after my brother tidied the cables. I have backups, but I would rather not buy a new computer.'),
 'Storage upgrade':('Room for my projects',180,'My 480 GB drive works, but I need at least 1 TB for university projects. I have backed up my files; please fit a larger SATA SSD.'),
 'Checkup':('Second opinion',90,'An advert said my PC has hardware problems. It seems to run normally. Please test it before spending money on replacement parts.'),
}
KINDS=tuple(REQUESTS)
# Deterministic rotation is stable across reloads. Memory is a single desktop DIMM;
# every SATA drive and GPU below uses the existing hands-on service procedure.
PROFILES=(
 {'Case':'case4000','CPU':'i5','Motherboard':'b560','GPU':'rx6600','PSU':'cx550','RAM':'replacement','Storage':'a400'},
 {'Case':'h510','CPU':'ryzen5600','Motherboard':'b550','GPU':'rx6600','PSU':'cx650','RAM':'replacement','Storage':'mx500'},
 {'Case':'focusg','CPU':'i7','Motherboard':'b560','GPU':'gtx1650','PSU':'cx550','RAM':'crucial16','Storage':'a400'},
 {'Case':'case4000','CPU':'ryzen5700','Motherboard':'b550','GPU':'rtx3060','PSU':'cx750','RAM':'lpx16','Storage':'evo870','Cooler':'pure_rock'},
 {'Case':'focusg','CPU':'i3','Motherboard':'b560','GPU':'gtx1650','PSU':'cx550','RAM':'crucial8','Storage':'mx500'},
 {'Case':'h510','CPU':'i511400','Motherboard':'b560','GPU':'rtx2060','PSU':'cx650','RAM':'upgrade','Storage':'evo500'},
 {'Case':'case4000','CPU':'ryzen3600','Motherboard':'b550','GPU':'rx580','PSU':'cx650','RAM':'lpx8','Storage':'mx500tb'},
 {'Case':'focusg','CPU':'i5','Motherboard':'b560','GPU':'rx580','PSU':'cx550','RAM':'lpx16','Storage':'evo500'},
 {'Case':'h510','CPU':'ryzen5600','Motherboard':'b550','GPU':'rtx3060','PSU':'cx650','RAM':'crucial16','Storage':'a400','Cooler':'pure_rock'},
 {'Case':'case4000','CPU':'i7','Motherboard':'b560','GPU':'rtx2060','PSU':'cx750','RAM':'upgrade','Storage':'evo870'},
 {'Case':'focusg','CPU':'ryzen3600','Motherboard':'b550','GPU':'gtx1650','PSU':'cx550','RAM':'crucial8','Storage':'mx500'},
 {'Case':'h510','CPU':'i3','Motherboard':'b560','GPU':'rx6600','PSU':'cx550','RAM':'lpx8','Storage':'evo500'},
 {'Case':'case4000','CPU':'i511400','Motherboard':'b560','GPU':'rtx3060','PSU':'cx650','RAM':'lpx16','Storage':'mx500tb','Cooler':'pure_rock'},
 {'Case':'focusg','CPU':'ryzen5700','Motherboard':'b550','GPU':'rx580','PSU':'cx750','RAM':'upgrade','Storage':'evo870','Cooler':'pure_rock'},
 {'Case':'h510','CPU':'i7','Motherboard':'b560','GPU':'gtx1650','PSU':'cx650','RAM':'crucial16','Storage':'a400'},
 {'Case':'case4000','CPU':'ryzen5600','Motherboard':'b550','GPU':'rtx2060','PSU':'cx550','RAM':'lpx8','Storage':'mx500'},
 {'Case':'focusg','CPU':'i511400','Motherboard':'b560','GPU':'rx6600','PSU':'cx650','RAM':'crucial8','Storage':'evo500'},
)
