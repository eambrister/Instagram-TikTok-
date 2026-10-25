// Settings shared by every video in this project.
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;

// Instagram/TikTok UI covers the edges (action buttons on the right, caption at the bottom).
// Keep all important text and graphics inside x = 120 to x = 960.
export const SAFE_LEFT = 120;
export const SAFE_RIGHT = 960;
export const SAFE_WIDTH = SAFE_RIGHT - SAFE_LEFT;

// The source clip. Never modify this file; effects only read it.
export const SOURCE_CLIP = "talking.mp4";
