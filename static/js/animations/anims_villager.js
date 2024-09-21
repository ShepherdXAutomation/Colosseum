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
        key: 'villager-walk-right',
        frames: scene.anims.generateFrameNames('villager_sprite', {
            start: 90,  // Starting frame number
            end: 97,    // Ending frame number
            prefix: 'villager_sprite-',  // Prefix for each frame
            suffix: '.png'  // File extension
        }),
        frameRate: 7,  // Adjust the frame rate as needed
        repeat: -1  // Loop the animation
    });
    scene.anims.create({
        key: 'villager-walk-down',
        frames: scene.anims.generateFrameNames('villager_sprite', {
            start: 81,  // Starting frame number
            end: 88,    // Ending frame number
            prefix: 'villager_sprite-',  // Prefix for each frame
            suffix: '.png'  // File extension
        }),
        frameRate: 4,  // Adjust the frame rate as needed
        repeat: -1  // Loop the animation
    });
    scene.anims.create({
        key: 'villager-walk-left',
        frames: scene.anims.generateFrameNames('villager_sprite', {
            start: 72,  // Starting frame number
            end: 79,    // Ending frame number
            prefix: 'villager_sprite-',  // Prefix for each frame
            suffix: '.png'  // File extension
        }),
        frameRate: 4,  // Adjust the frame rate as needed
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
    scene.anims.create({
        key: 'villager-idle-right',
        frames: scene.anims.generateFrameNames('villager_sprite', {
            start: 89,  // Starting frame number
            end: 89,    // Ending frame number
            prefix: 'villager_sprite-',  // Prefix for each frame
            suffix: '.png'  // File extension
        }),
        frameRate: 4,  // Adjust the frame rate as needed
        repeat: -1  // Loop the animation
    });
    scene.anims.create({
        key: 'villager-idle-down',
        frames: scene.anims.generateFrameNames('villager_sprite', {
            start: 80,  // Starting frame number
            end: 80,    // Ending frame number
            prefix: 'villager_sprite-',  // Prefix for each frame
            suffix: '.png'  // File extension
        }),
        frameRate: 4,  // Adjust the frame rate as needed
        repeat: -1  // Loop the animation
    });
    scene.anims.create({
        key: 'villager-idle-left',
        frames: scene.anims.generateFrameNames('villager_sprite', {
            start: 71,  // Starting frame number
            end: 71,    // Ending frame number
            prefix: 'villager_sprite-',  // Prefix for each frame
            suffix: '.png'  // File extension
        }),
        frameRate: 4,  // Adjust the frame rate as needed
        repeat: -1  // Loop the animation
    });
}
