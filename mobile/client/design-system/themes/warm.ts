/**
 * 起了吗 App - 温暖守护主题
 * Warm Guardian Theme
 *
 * 配色：晨光橙 + 生命绿
 * 特点：高对比度、大触摸目标、温暖人文感
 */
import { Theme, ThemeConfig } from '../types';
import { lightColors, darkColors } from '../tokens/colors';
import { typography } from '../tokens/typography';
import { spacing } from '../tokens/spacing';
import { borderRadius } from '../tokens/borderRadius';
import { createShadows } from '../tokens/shadows';
import { animation } from '../tokens/animation';
import { touchTarget, hitSlop, breakpoints, zIndex } from '../tokens/layout';
import { interaction } from '../tokens/interaction';
import { componentDefaults } from '../tokens/componentDefaults';

function createTheme(colors: typeof lightColors): Theme {
  return {
    colors,
    typography,
    spacing,
    borderRadius,
    shadows: createShadows(colors.shadow, colors.shadowStrong),
    animation,
    touchTarget,
    hitSlop,
    breakpoints,
    zIndex,
    interaction,
    componentDefaults,
  };
}

export const warmLight = createTheme(lightColors);
export const warmDark = createTheme(darkColors);

export const warmThemeConfig: ThemeConfig = {
  light: warmLight,
  dark: warmDark,
};
