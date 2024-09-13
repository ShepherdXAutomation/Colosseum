export function createAnimations(scene) {
    scene.anims.create({
        key: 'fairy-whip',
        frames: scene.anims.generateFrameNames('strongfairy', {
            start: 371,
            end: 378,
            prefix: 'strongfairy',
            suffix: '.png'
        }),
        frameRate: 10,
        repeat: -1
    });

    scene.anims.create({
        key: 'fairy-walk-down',
        frames: scene.anims.generateFrameNames('strongfairy', {
            start: 80,
            end: 86,
            prefix: 'strongfairy',
            suffix: '.png'
        }),
        frameRate: 10,
        repeat: -1
    });

    scene.anims.create({
        key: 'fairy-dance',
        frames: scene.anims.generateFrameNames('strongfairy', {
            start: 108,
            end: 113,
            prefix: 'strongfairy',
            suffix: '.png'
        }),
        frameRate: 10,
        repeat: -1
    });

    scene.anims.create({
        key: 'fairy-idle',
        frames: scene.anims.generateFrameNames('strongfairy', {
            start: 174,
            end: 175,
            prefix: 'strongfairy',
            suffix: '.png'
        }),
        frameRate: 2,
        repeat: -1
    });

    scene.anims.create({
        key: 'idle',
        frames: scene.anims.generateFrameNumbers('character', { start: 1, end: 1 }), 
        frameRate: 8,
        repeat: -1
    });

    scene.anims.create({
        key: 'villager-walk',
        frames: scene.anims.generateFrameNumbers('character', { start: 62, end: 68 }),
        frameRate: 8,
        repeat: -1
    });

    scene.anims.create({
        key: 'nostalgia-enemy-walk-up',
        frames: scene.anims.generateFrameNumbers('enemy', { start: 2, end: 8 }),
        frameRate: 9,
        repeat: -1
    });

    scene.anims.create({
        key: 'nostalgia-enemy-idle-left',
        frames: scene.anims.generateFrameNumbers('enemy', { start: 9, end: 9 }),
        frameRate: 8,
        repeat: -1
    });

    scene.anims.create({
        key: 'run',
        frames: scene.anims.generateFrameNumbers('character', { start: 8, end: 11 }), 
        frameRate: 12,
        repeat: -1
    });

    scene.anims.create({
        key: 'attack1',
        frames: scene.anims.generateFrameNumbers('character', { start: 12, end: 15 }), 
        frameRate: 10,
        repeat: -1
    });

    scene.anims.create({
        key: 'attack2',
        frames: scene.anims.generateFrameNumbers('character', { start: 16, end: 19 }), 
        frameRate: 10,
        repeat: -1
    });
}
export function setupSoundEvents(scene, character, soundConfig) {
    character.on('animationupdate', function (animation, frame) {
        const animKey = animation.key;
        const frameIndex = frame.index;

        // Check if the current animation and frame match any in the sound config
        if (soundConfig[animKey] && soundConfig[animKey][frameIndex]) {
            const sound = soundConfig[animKey][frameIndex];
            sound.play();  // Play the assigned sound
        }
    });
}
