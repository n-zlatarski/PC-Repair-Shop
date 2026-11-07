"""Twelve wardrobe and silhouette profiles shared by customers and pedestrians."""
SKINS=[(.64,.43,.32,1),(.78,.58,.44,1),(.42,.27,.20,1),(.57,.37,.27,1),(.83,.66,.53,1),(.31,.20,.16,1)]
HAIR=[(.055,.038,.028,1),(.16,.09,.05,1),(.27,.19,.11,1),(.08,.065,.057,1),(.36,.31,.25,1),(.065,.046,.035,1)]
STYLES=[('overshirt',(.30,.34,.28,1),(.095,.12,.15,1),'sidepart',.97,.98),('blazer',(.22,.24,.28,1),(.11,.11,.13,1),'bob',.93,.94),('hoodie',(.43,.42,.39,1),(.12,.15,.19,1),'crop',1.06,1.03),('jacket',(.29,.21,.15,1),(.13,.16,.18,1),'receding',1.12,1.01),('knit',(.42,.32,.25,1),(.16,.17,.18,1),'ponytail',.93,.97),('polo',(.13,.22,.28,1),(.22,.21,.18,1),'curly',1.04,1.02),('jacket',(.18,.23,.20,1),(.11,.14,.18,1),'crop',1.10,1.04),('blazer',(.18,.22,.28,1),(.17,.18,.21,1),'sidepart',1.0,.99),('hoodie',(.40,.25,.21,1),(.15,.16,.16,1),'curly',.98,.96),('overshirt',(.24,.29,.36,1),(.22,.20,.17,1),'receding',1.15,1.02),('knit',(.29,.32,.22,1),(.14,.17,.20,1),'bob',.96,.95),('polo',(.34,.25,.22,1),(.12,.13,.15,1),'ponytail',.98,1.0)]
def style(index,tag=''):
 outfit,cloth,trousers,haircut,width,height=STYLES[index%len(STYLES)]
 if tag=='delivery':outfit='courier';cloth=(.055,.24,.26,1);trousers=(.09,.12,.14,1);haircut='crop'
 return dict(outfit=outfit,cloth=cloth,trousers=trousers,haircut=haircut,width=width,height=height,skin=SKINS[index%len(SKINS)],hair=HAIR[(index*5)%len(HAIR)],feminine=index%12 in (1,4,10,11))
