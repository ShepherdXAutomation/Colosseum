export function createAnimations_dog(scene) {
    scene.anims.create({
    key: 'dog-walk-up',
    frames: scene.anims.generateFrameNames('dog_sprite', {
        start: 8,  // Starting frame number
        end: 11,    // Ending frame number
        prefix: 'dog_sprite-',  // Prefix for each frame
        suffix: '.png'  // File extension
    }),
    frameRate: 8,  // Adjust the frame rate as needed
    repeat: -1  // Loop the animation
});
scene.anims.create({
    key: 'dog-idle-up',
    frames: scene.anims.generateFrameNames('dog_sprite', {
        start: 8,  // Starting frame number
        end: 8,    // Ending frame number
        prefix: 'dog_sprite-',  // Prefix for each frame
        suffix: '.png'  // File extension
    }),
    frameRate: 4,  // Adjust the frame rate as needed
    repeat: -1  // Loop the animation
});
}
