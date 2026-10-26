import React from "react";
import { Composition } from "remotion";
import { FPS, HEIGHT, WIDTH } from "./settings";
import { SafeZoneGuide } from "./compositions/SafeZoneGuide";
import { BehindMeTest } from "./compositions/BehindMeTest";
import { OverTheShoulder, overTheShoulderDefaults } from "./compositions/OverTheShoulder";
import { GlassGraph, glassGraphDefaults } from "./compositions/GlassGraph";
import { FreezeFrame, freezeFrameDefaults } from "./compositions/FreezeFrame";
import { TierList, tierListDefaults } from "./compositions/TierList";
import { TextBehind, textBehindDefaults } from "./compositions/TextBehind";
import { ColorGrade, colorGradeDefaults } from "./compositions/ColorGrade";
import { ChatRender, chatRenderDefaults, chatRenderMetadata } from "./compositions/ChatRender";
import { FullReel, fullReelDefaults, fullReelMetadata } from "./compositions/FullReel";
import { ReelTextBehind, reelTextBehindDefaults, reelTextBehindMetadata } from "./compositions/ReelTextBehind";
import { StyledReel, styledReelDefaults, styledReelMetadata } from "./compositions/StyledReel";

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
      <Composition
        id="BehindMeTest"
        component={BehindMeTest}
        durationInFrames={FPS * 6}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="OverTheShoulder"
        component={OverTheShoulder}
        durationInFrames={84}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={overTheShoulderDefaults}
      />
      <Composition
        id="GlassGraph"
        component={GlassGraph}
        durationInFrames={90}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={glassGraphDefaults}
      />
      <Composition
        id="FreezeFrame"
        component={FreezeFrame}
        durationInFrames={90}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={freezeFrameDefaults}
      />
      <Composition
        id="TierList"
        component={TierList}
        durationInFrames={90}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={tierListDefaults}
      />
      <Composition
        id="TextBehind"
        component={TextBehind}
        durationInFrames={90}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={textBehindDefaults}
      />
      <Composition
        id="ColorGrade"
        component={ColorGrade}
        durationInFrames={90}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={colorGradeDefaults}
      />
      <Composition
        id="ChatRender"
        component={ChatRender}
        durationInFrames={165}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={chatRenderDefaults}
        calculateMetadata={chatRenderMetadata}
      />
      <Composition
        id="FullReel"
        component={FullReel}
        durationInFrames={1068}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={fullReelDefaults}
        calculateMetadata={fullReelMetadata}
      />
      <Composition
        id="ReelTextBehind"
        component={ReelTextBehind}
        durationInFrames={300}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={reelTextBehindDefaults}
        calculateMetadata={reelTextBehindMetadata}
      />
      <Composition
        id="StyledReel"
        component={StyledReel}
        durationInFrames={1274}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={styledReelDefaults}
        calculateMetadata={styledReelMetadata}
      />
    </>
  );
};
