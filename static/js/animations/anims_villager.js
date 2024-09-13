export function createAnimations_villager(scene) {
        scene.anims.create({
        key: 'villager-walk-up',
        frames: scene.anims.generateFrameNames('villager_sprite', {
            start: 63,  // Starting frame number
            end: 70,    // Ending frame number
            prefix: 'villager_sprite-',  // Prefix for each frame
            suffix: '.png'  // File extension
        }),
        frameRate: 8,  // Adjust the frame rate as needed
        repeat: -1  // Loop the animation
    });
    scene.anims.create({
        key: 'villager-idle-up',
        frames: scene.anims.generateFrameNames('villager_sprite', {
            start: 62,  // Starting frame number
            end: 62,    // Ending frame number
            prefix: 'villager_sprite-',  // Prefix for each frame
            suffix: '.png'  // File extension
        }),
        frameRate: 4,  // Adjust the frame rate as needed
        repeat: -1  // Loop the animation
    });
}
