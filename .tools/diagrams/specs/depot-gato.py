from svgdiagram import Bars, Flow

PAGE = "work/games/depot-gato.html"

scenes = (
    Flow("dg-scenes", "Scene tree and signals",
         "main.tscn holds the level, the containers for towers, enemies and projectiles, the placement and wave "
         "nodes, and the HUD. Enemies, towers and projectiles are separate scenes instanced at runtime. GameState is "
         "an autoload; the HUD only listens to its signals.", cols=4)
    .group("main.tscn", rows=(0, 1), cols=(0, 3), color="grey")
    .node("level", "Level", "TileMapLayer built from the ASCII map, navigation on path tiles", at=(0, 0), span=2, color="green")
    .node("place", "TowerPlacement", "ghost, build, sell", at=(0, 2), color="blue")
    .node("waves", "WaveManager", "reads WaveData, spawns, counts", at=(0, 3), color="orange")
    .node("hud", "HUD", "CanvasLayer, labels and palette", at=(1, 0), color="purple")
    .node("proj", "Projectiles", "kibble, fish, yarn", at=(1, 1), color="yellow")
    .node("towers", "Towers", "instanced tower scenes", at=(1, 2), color="cyan")
    .node("enemies", "Enemies", "instanced enemy scenes", at=(1, 3), color="red")
    .node("gs", "GameState autoload", "coins, lives, wave; currency_changed, lives_changed, wave_changed, game_over", at=(2, 1), span=2, color="purple")
    .edge("place", "towers", "instance", exit="b", enter="t", bend=0)
    .edge("waves", "enemies", "instance")
    .edge("enemies", "gs", "died, reached depot")
    .edge("gs", "hud", "signals")
)

states = (
    Flow("dg-states", "Enemy state machine",
         "Each enemy waits in IDLE until the navigation map has synced, walks the path in WALKING, and leaves either "
         "through ATTACKING (it reached the depot and costs lives) or DEAD (it pays its reward and plays the death "
         "animation).", cols=4)
    .node("idle", "IDLE", "spawned; wait for the navigation map to sync", at=(0, 0), color="grey")
    .node("walk", "WALKING", "follow NavigationAgent2D, walk animation loops", at=(0, 1), span=2, color="blue")
    .node("att", "ATTACKING", "reached the depot: lose lives, free", at=(0, 3), color="red")
    .node("dead", "DEAD", "reward paid, death animation, free", at=(1, 1), span=2, color="green")
    .edge("idle", "walk", "map ready")
    .edge("walk", "att", "within 6 px of depot")
    .edge("walk", "dead", "hp reaches 0")
)

loop = (
    Flow("dg-loop", "One round",
         "The player builds between waves. A wave spawns its entries one by one; towers shoot what is in range; each "
         "enemy either dies (coins) or reaches the depot (lives). When the last enemy of a wave is gone, a bonus is "
         "paid and a six-second countdown starts the next wave, until the eighth is held or the lives run out.",
         cols=4)
    .node("build", "Build", "spend coins on cats", at=(0, 0), color="cyan")
    .node("spawn", "Wave spawns", "entries from WaveData", at=(0, 1), color="orange")
    .node("fight", "Towers fire", "target closest to the depot", at=(0, 2), color="blue")
    .node("res", "Each enemy", "dies: coins / gets through: lives", at=(0, 3), color="yellow")
    .node("lose", "Lives at 0", "The depot fell", at=(1, 2), color="red")
    .node("clear", "Wave cleared", "bonus, then a 6 s countdown back to Build", at=(1, 3), color="green")
    .node("win", "Wave 8 held", "Depot saved", at=(2, 3), color="green")
    .edge("build", "spawn").edge("spawn", "fight").edge("fight", "res").edge("res", "clear")
    .edge("res", "lose", exit="b", enter="t", bend=0)
    .edge("clear", "win", "after wave 8")
)

hp = (
    Bars("dg-enemy-hp", "Enemy health at wave strength",
         "Base health from enemy.gd times each wave's health scale, for the toughest appearance of each enemy. "
         "These are the game's own numbers.", unit=" HP,", max_value=220)
    .bar("Mouse, wave 1", 14, "speed 34", color="blue")
    .bar("Mouse, wave 8", 25.2, "14 x 1.8", color="blue")
    .bar("Rat, wave 3", 45, "speed 22", color="orange")
    .bar("Rat, wave 8", 67.5, "45 x 1.5", color="orange")
    .bar("Armored rat, wave 6", 160, "speed 15", color="red")
    .bar("Armored rat, wave 8", 208, "160 x 1.3", color="red")
)

waves = (
    Bars("dg-waves", "Enemies per wave",
         "Counted from data/waves/*.tres. Waves 6 to 8 add armored rats, which cost 5 lives each if they get through.",
         unit=" enemies:", max_value=55)
    .bar("Wave 1", 8, "mice only", color="blue")
    .bar("Wave 2", 12, "mice only", color="blue")
    .bar("Wave 3", 12, "8 mice, 4 rats", color="blue")
    .bar("Wave 4", 10, "rats only", color="orange")
    .bar("Wave 5", 22, "16 mice, 6 rats", color="orange")
    .bar("Wave 6", 12, "2 armored, 10 rats", color="red")
    .bar("Wave 7", 30, "20 mice, 8 rats, 2 armored", color="red")
    .bar("Wave 8", 37, "12 rats, 5 armored, 20 mice", color="red")
)

DIAGRAMS = [scenes, states, loop, hp, waves]
