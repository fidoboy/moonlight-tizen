function remoteControllerHandler(e) {
  isGamepadActive = false;
  const keyCode = e.keyCode;

  if (!isInGame && isStartupUiRestored &&
      [tvKey.KEY_UP, tvKey.KEY_DOWN, tvKey.KEY_LEFT, tvKey.KEY_RIGHT,
       tvKey.KEY_ENTER, tvKey.KEY_REMOTE_ENTER, tvKey.KEY_RETURN].indexOf(keyCode) !== -1) {
    isStartupHostFocusResolved = true;
  }

  switch (keyCode) {
    case tvKey.KEY_UP:
      // Navigate in the up direction
      Navigation.up();
      break;
    case tvKey.KEY_DOWN:
      // Navigate in the down direction
      Navigation.down();
      break;
    case tvKey.KEY_LEFT:
      // Navigate in the left direction
      Navigation.left();
      break;
    case tvKey.KEY_RIGHT:
      // Navigate in the right direction
      Navigation.right();
      break;
    case tvKey.KEY_ENTER:
    case tvKey.KEY_REMOTE_ENTER:
      e.preventDefault(); // Prevent native asynchronous click
      // Select the current item
      Navigation.accept();
      break;
    case tvKey.KEY_RETURN:
      // Go back or cancel the operation
      Navigation.back();
      break;
    case tvKey.KEY_VOLUME_UP:
      // Increase the volume
      tizen.tvaudiocontrol.setVolumeUp();
      break;
    case tvKey.KEY_VOLUME_DOWN:
      // Decrease the volume
      tizen.tvaudiocontrol.setVolumeDown();
      break;
    case tvKey.KEY_VOLUME_MUTE:
      // Mute the volume
      tizen.tvaudiocontrol.setMute();
      break;
    case tvKey.KEY_CHANNEL_UP:
      // Triggers the press action
      Navigation.press();
      break;
    case tvKey.KEY_CHANNEL_DOWN:
      // Triggers the switch action
      Navigation.switch();
      break;
    case tvKey.KEY_RED:
      // Terminate the connection
      if (isInGame === true) {
        Module.stopStream();
      }
      break;
    case tvKey.KEY_YELLOW:
      // Toggle performance stats overlay
      if (isInGame === true) {
        Module.toggleStats();
      }
      break;
    default:
      break;
  }
}
