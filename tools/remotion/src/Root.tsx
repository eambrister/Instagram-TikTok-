import React from 'react';
import { Composition } from 'remotion';
import { FormCallout, formCalloutDefaults } from './FormCallout';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="FormCallout" component={FormCallout} durationInFrames={120} fps={30} width={1080} height={1920}
      defaultProps={formCalloutDefaults} />
  </>
);
