/**
 * US-011：自动化渲染性能回归（Reassure）
 * 与 app/(tabs)/_layout 底部 Tab 图标一致，避免引入 router/网络依赖。
 */
import React from 'react';
import { View } from 'react-native';
import { measureRenders } from 'reassure';
import { FontAwesome6 } from '@expo/vector-icons';

const TAB_ICONS = [
  'sun',
  'phone-volume',
  'address-book',
  'heart-pulse',
  'book-medical',
] as const;

function TabBarIconRow() {
  return (
    <View style={{ flexDirection: 'row', gap: 12 }}>
      {TAB_ICONS.map((name) => (
        <FontAwesome6 key={name} name={name} size={24} color="#78909C" />
      ))}
    </View>
  );
}

test('Tab bar icon row render cost (aligned with tabs layout)', async () => {
  await measureRenders(<TabBarIconRow />);
});
