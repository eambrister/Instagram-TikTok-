import { getInputProps } from "remotion";

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

// Size of talking.mp4 (horizontal 4K) and how it is framed in the vertical video.
export const CLIP_WIDTH = 3840;
export const CLIP_HEIGHT = 2160;
// How many source pixels fit across the 1080 px width. 2000 keeps head and shoulders in shot;
// lower is tighter. The clip sits at the bottom and plain wall fills the space above it.
export const FRAME_SOURCE_WIDTH = 2000;
// Horizontal position of the head in the clip, 0 to 1 (measured from the mask).
export const FRAME_CENTER_X = 0.6;

// Safe-zone audit: render with --props='{"audit":true}' to hide the footage and full-screen
// backgrounds, so only text and graphics are drawn (see tools/safe_zone_audit.py).
export const AUDIT = Boolean((getInputProps() as { audit?: boolean }).audit);
