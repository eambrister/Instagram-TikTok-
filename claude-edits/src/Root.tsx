import React from "react";
import { Composition } from "remotion";
import { FPS, HEIGHT, WIDTH } from "./settings";
import { SafeZoneGuide } from "./compositions/SafeZoneGuide";

// Every effect is registered here as its own composition, named after the effect.
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SafeZoneGuide"
        component={SafeZoneGuide}
        durationInFrames={FPS * 3}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
