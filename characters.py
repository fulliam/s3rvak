# characters.py

from models import Player, CharacterInfo, CharacterState, CharacterStats, CharacterInventory, Health, Mana, Stamina, Position, Params, Skill, Skills, Money, Crit, Attack

characters = {
    "Roh": Player(
        info=CharacterInfo(
            category='ally',
            character='wizard',
            location='default',
            level=1,
            experience=0,
            levelUpExperience=100
        ),
        state=CharacterState(
            position=Position(x=0, y=0),
            direction='right',
            action='idle',
            health=Health(max=100, current=100, recovery=2),
            mana=Mana(max=80, current=80, recovery=1.5),
            stamina=Stamina(max=50, current=50, recovery=1),
            armor=0
        ),
        stats=CharacterStats(
            speed={'walking': 2, 'running': 4},
            params=Params(strength=5, agility=5, intelligence=5, stamina=5, luck=5),
            skills=Skills(
                fireshtorm=Skill(damage=10, type='magic', range=300, level=0),
                lighting=Skill(damage=10, type='magic', range=500, level=0),
                poisonshtorm=Skill(damage=15, type='magic', range=500, level=0)
            ),
            skillPoints=0,
            statPoints=5,
            damage={'physic': 1, 'magic': 1},
            attacks={
                'attack': Attack(damage=8, type='physic', range=100, level=1),
                'attack2': Attack(damage=10, type='physic', range=100, level=1),
                'attack3': Attack(damage=16, type='physic', range=100, level=1)
            },
            attackSpeed=1,
            crit=Crit(chance=0.1, factor=1.5)
        ),
        inventory=CharacterInventory(
            money=Money(coins={'silver': 0, 'gold': 0, 'red': 0},
                        gems={'blue': 0, 'yellow': 0, 'green': 0, 'grey': 0, 'red': 0}),
            inventory=[]
        )
    ),

    "Kelly": Player(
        info=CharacterInfo(
            category='ally',
            character='skeleton',
            location='default',
            level=1,
            experience=0,
            levelUpExperience=100
        ),
        state=CharacterState(
            position=Position(x=0, y=0),
            direction='left',
            action='idle',
            health=Health(max=100, current=100, recovery=2),
            mana=Mana(max=80, current=80, recovery=1.5),
            stamina=Stamina(max=50, current=50, recovery=1),
            armor=0
        ),
        stats=CharacterStats(
            speed={'walking': 2, 'running': 4},
            params=Params(strength=5, agility=5, intelligence=5, stamina=5, luck=5),
            skills=Skills(
                fireshtorm=Skill(damage=10, type='magic', range=300, level=0),
                lighting=Skill(damage=10, type='magic', range=500, level=0),
                poisonshtorm=Skill(damage=15, type='magic', range=500, level=0)
            ),
            skillPoints=0,
            statPoints=5,
            damage={'physic': 1, 'magic': 1},
            attacks={
                'attack': Attack(damage=8, type='physic', range=100, level=1),
                'attack2': Attack(damage=10, type='physic', range=100, level=1),
                'attack3': Attack(damage=16, type='physic', range=100, level=1)
            },
            attackSpeed=1,
            crit=Crit(chance=0.1, factor=1.5)
        ),
        inventory=CharacterInventory(
            money=Money(coins={'silver': 0, 'gold': 0, 'red': 0},
                        gems={'blue': 0, 'yellow': 0, 'green': 0, 'grey': 0, 'red': 0}),
            inventory=[]
        )
    ),
}
