"""Real product identities; fictional training prices, original simplified models."""
def item(name,category,price,spec,**extra):
    return dict(name=name,category=category,price=price,spec=spec,faulty=False,**extra)
PARTS={
 'original':item('Kingston FURY Beast 8 GB','RAM',0,'Customer module / DDR4-3200',capacity=8,ddr=4),
 'replacement':item('Kingston FURY Beast 8 GB','RAM',25,'1 x 8 GB / DDR4-3200',capacity=8,ddr=4),
 'upgrade':item('Kingston FURY Beast 16 GB','RAM',45,'1 x 16 GB / DDR4-3200',capacity=16,ddr=4),
 'incompatible':item('Kingston FURY Beast DDR5','RAM',55,'1 x 16 GB / DDR5-5200',capacity=16,ddr=5),
 'rx6600':item('SAPPHIRE PULSE Radeon RX 6600','GPU',185,'8 GB GDDR6 / PCIe / 8-pin power'),
 'gtx1650':item('GIGABYTE GTX 1650 WINDFORCE','GPU',110,'4 GB GDDR5 / PCIe / 6-pin power'),
 'a400':item('Kingston A400 480 GB','Storage',35,'2.5-inch SATA / 480 GB',capacity=480),
 'evo870':item('Samsung 870 EVO 1 TB','Storage',65,'2.5-inch SATA / 1 TB',capacity=1000),
 'i5':item('Intel Core i5-10400F','CPU',95,'6 cores / 12 threads / LGA1200'),
 'i7':item('Intel Core i7-10700','CPU',155,'8 cores / 16 threads / LGA1200'),
 'b560':item('ASUS PRIME B560-PLUS','Motherboard',95,'ATX / LGA1200 / DDR4'),
 'cx550':item('Corsair CX550','PSU',50,'550 W / ATX / 80 PLUS Bronze'),
 'cx650':item('Corsair CX650','PSU',65,'650 W / ATX / 80 PLUS Bronze'),
 'freezer':item('ARCTIC Freezer 7 X CO','Cooler',25,'Air cooler / includes LGA1200 support'),
 'p12':item('ARCTIC P12 PWM','Fan',10,'120 mm / 4-pin PWM'),
 'case4000':item('Corsair 4000D AIRFLOW','Case',85,'ATX mid tower / black'),
}
PARTS.update({
 'ryzen5600':item('AMD Ryzen 5 5600','CPU',110,'6 cores / 12 threads / AM4'),
 'b550':item('ASUS PRIME B550-PLUS','Motherboard',95,'ATX / AM4 / DDR4 / compatible BIOS required'),
 'h510':item('NZXT H510','Case',80,'ATX mid tower / white and black'),
 'focusg':item('Fractal Design Focus G','Case',60,'ATX mid tower / mesh / optical bays'),
})
# Additional compatible training configurations. Prices are fictional, not quotations.
PARTS.update({
 'lpx8':item('Corsair Vengeance LPX 8 GB','RAM',28,'1 x 8 GB / DDR4-3200',capacity=8,ddr=4,brand='CORSAIR',model='VENGEANCE LPX',style='lpx'),
 'lpx16':item('Corsair Vengeance LPX 16 GB','RAM',48,'1 x 16 GB / DDR4-3200',capacity=16,ddr=4,brand='CORSAIR',model='VENGEANCE LPX',style='lpx'),
 'crucial8':item('Crucial Desktop Memory 8 GB','RAM',24,'1 x 8 GB / DDR4-3200',capacity=8,ddr=4,brand='CRUCIAL',model='DDR4 UDIMM',style='bare'),
 'crucial16':item('Crucial Desktop Memory 16 GB','RAM',43,'1 x 16 GB / DDR4-3200',capacity=16,ddr=4,brand='CRUCIAL',model='DDR4 UDIMM',style='bare'),
 'rtx3060':item('MSI GeForce RTX 3060 VENTUS 2X','GPU',225,'12 GB GDDR6 / PCIe / 8-pin power',brand='MSI',model='GEFORCE RTX 3060',style='ventus',pins=8),
 'rtx2060':item('MSI GeForce RTX 2060 VENTUS','GPU',155,'6 GB GDDR6 / PCIe / 8-pin power',brand='MSI',model='GEFORCE RTX 2060',style='ventus',pins=8),
 'rx580':item('SAPPHIRE PULSE Radeon RX 580','GPU',95,'8 GB GDDR5 / PCIe / 8-pin power',brand='SAPPHIRE',model='RADEON RX 580',style='pulse',pins=8),
 'mx500':item('Crucial MX500 500 GB','Storage',38,'2.5-inch SATA / 500 GB',capacity=500,brand='CRUCIAL',model='MX500',style='silver'),
 'mx500tb':item('Crucial MX500 1 TB','Storage',64,'2.5-inch SATA / 1 TB',capacity=1000,brand='CRUCIAL',model='MX500',style='silver'),
 'evo500':item('Samsung 870 EVO 500 GB','Storage',40,'2.5-inch SATA / 500 GB',capacity=500,brand='SAMSUNG',model='870 EVO',style='samsung'),
 'i3':item('Intel Core i3-10100F','CPU',65,'4 cores / 8 threads / LGA1200',brand='INTEL',model='i3-10100F',socket='LGA1200'),
 'i511400':item('Intel Core i5-11400F','CPU',105,'6 cores / 12 threads / LGA1200',brand='INTEL',model='i5-11400F',socket='LGA1200'),
 'ryzen3600':item('AMD Ryzen 5 3600','CPU',85,'6 cores / 12 threads / AM4',brand='AMD',model='Ryzen 5 3600',socket='AM4'),
 'ryzen5700':item('AMD Ryzen 7 5700X','CPU',145,'8 cores / 16 threads / AM4',brand='AMD',model='Ryzen 7 5700X',socket='AM4'),
 'cx750':item('Corsair CX750','PSU',75,'750 W / ATX / 80 PLUS Bronze',brand='CORSAIR',model='CX750'),
 'pure_rock':item('be quiet! Pure Rock 2','Cooler',35,'Tower air cooler / AM4 and LGA1200 mounting kits',brand='be quiet!',model='Pure Rock 2',style='tower'),
})
# One product identity drives its installed model, stock card, package and faulty alias.
for key,source in [('original','replacement'),('faulty_gpu','rx6600'),('faulty_storage','a400')]:
    PARTS[key]=dict(PARTS[source],faulty=True,price=0,source=source)
for key,p in list(PARTS.items()):
    if p['category'] in ('RAM','GPU','Storage') and not p['faulty'] and key!='incompatible':
        PARTS['fault_'+key]=dict(p,faulty=True,price=0,source=key)
CATEGORIES=['All','RAM','GPU','Storage','CPU','Motherboard','PSU','Cooler','Fan','Case']
SERVICEABLE={'RAM','GPU','Storage'}
DEFAULT_HARDWARE={'GPU':'rx6600','Storage':'a400','CPU':'i5','Motherboard':'b560','PSU':'cx550','Cooler':'freezer','Fan':'p12','Case':'case4000'}
PEOPLE=['Maya','Daniel','Elena','Boris','Sofia','Viktor','Nadia','Ivan','Mira','Alex','Petar','Lina']
LESSONS={
 'RAM':'RAM temporarily holds data used by running programs. Capacity affects how much work can stay in memory. DDR is the memory generation: DDR4 and DDR5 are not interchangeable. Open both latches and align the notch; never force a module.',
 'GPU':'The graphics card renders images. Release the PCIe retention latch and bracket screw before lifting it out. Disconnect its power cable first. Check the slot, power supply and case clearance when choosing a replacement.',
 'Storage':'An SSD retains files when power is off. A 2.5-inch SATA drive needs both a SATA data cable and power. Disconnect both before removal. A hardware test does not clone files: real repairs require a backup and data migration.',
 'CPU':'The processor executes instructions. Socket, chipset and firmware support all matter. Intel PCs here use LGA1200; Ryzen PCs use AM4. Those sockets are not interchangeable. The CPU is inspection-only. To renew paste, disconnect power, lift the cooler, clean old paste, apply a small fresh dot and refit the cooler.',
 'Motherboard':'The motherboard connects all components. B560 uses LGA1200; B550 uses AM4. Both training platforms use DDR4 desktop DIMMs. Firmware and exact memory support still need checking in real repairs.',
 'PSU':'The power supply converts mains power to DC. Match connectors and power requirements. Never open its enclosure. PSU replacement is not enabled in this build.',
}
