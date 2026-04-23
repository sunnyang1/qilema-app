/**
 * 知识库页面（增强版）
 * 改进：
 * - 搜索框聚焦动画
 * - 分类横滑带选中高亮
 * - 文章卡片色彩标签 + 阅读时间
 * - 热门推荐视觉
 */
import React, { useState, useRef, useCallback } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  Animated,
  ScrollView,
  useWindowDimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { FontAwesome6 } from '@expo/vector-icons';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import EmptyState from '@/components/EmptyState';
import { useTheme } from '@/hooks/useTheme';
import type { CreateStylesTheme } from '@/design-system';
import { usePressScale } from '@/hooks/usePressScale';
import { spacing, borderRadius } from '@/design-system';
import { useSafeRouter } from '@/hooks/useSafeRouter';

interface Category {
  id: string;
  name: string;
  icon: string;
  articleCount: number;
  gradient: [string, string];
}

interface Article {
  id: string;
  title: string;
  summary: string;
  category: string;
  categoryName: string;
  readTime: string;
  isHot?: boolean;
  tagColor: string;
}

const CATEGORIES: Category[] = [
  { id: 'all', name: '全部', icon: 'border-all', articleCount: 79, gradient: ['#667eea', '#764ba2'] },
  { id: 'emergency', name: '急救知识', icon: 'truck-medical', articleCount: 12, gradient: ['#EF5350', '#B71C1C'] },
  { id: 'health', name: '健康常识', icon: 'heart-pulse', articleCount: 24, gradient: ['#66BB6A', '#2E7D32'] },
  { id: 'chronic', name: '慢性病', icon: 'lungs', articleCount: 18, gradient: ['#FF8A65', '#BF360C'] },
  { id: 'elderly', name: '老年护理', icon: 'person-cane', articleCount: 15, gradient: ['#FFA726', '#E65100'] },
  { id: 'prevention', name: '疾病预防', icon: 'shield-heart', articleCount: 20, gradient: ['#29B6F6', '#01579B'] },
];

const ARTICLES: Article[] = [
  {
    id: '1',
    title: '心肺复苏（CPR）步骤详解',
    summary: '掌握正确的心肺复苏方法，关键时刻能救命。包含成人与儿童的操作差异。',
    category: 'emergency',
    categoryName: '急救知识',
    readTime: '5分钟',
    isHot: true,
    tagColor: '#EF5350',
  },
  {
    id: '2',
    title: '高血压患者的日常注意事项',
    summary: '科学管理血压，预防并发症，这些生活细节至关重要。',
    category: 'chronic',
    categoryName: '慢性病',
    readTime: '8分钟',
    isHot: true,
    tagColor: '#FF8A65',
  },
  {
    id: '3',
    title: '独居老人安全指南',
    summary: '全面保障独居老人的安全，从环境布置到紧急联络的完整指南。',
    category: 'elderly',
    categoryName: '老年护理',
    readTime: '10分钟',
    tagColor: '#FFA726',
  },
  {
    id: '4',
    title: '常见急救药物使用指南',
    summary: '正确使用急救药物，避免误用。家庭必备急救箱清单。',
    category: 'emergency',
    categoryName: '急救知识',
    readTime: '6分钟',
    tagColor: '#EF5350',
  },
  {
    id: '5',
    title: '如何识别脑卒中的早期症状',
    summary: '掌握脑卒中的"FAST"判断法，及时识别和处理。',
    category: 'emergency',
    categoryName: '急救知识',
    readTime: '4分钟',
    isHot: true,
    tagColor: '#EF5350',
  },
  {
    id: '6',
    title: '老年人防跌倒综合指南',
    summary: '跌倒是老年人受伤的主要原因，这份指南帮助预防意外。',
    category: 'elderly',
    categoryName: '老年护理',
    readTime: '7分钟',
    tagColor: '#FFA726',
  },
];

export default function KnowledgeScreen() {
  const { theme } = useTheme();
  const router = useSafeRouter();
  const { width } = useWindowDimensions();

  const [searchQuery, setSearchQuery] = useState('');
  const [searchFocused, setSearchFocused] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');

  const searchBarWidth = useRef(new Animated.Value(1)).current;

  const onSearchFocus = () => {
    setSearchFocused(true);
    Animated.spring(searchBarWidth, { toValue: 1.02, useNativeDriver: true, speed: 50 }).start();
  };
  const onSearchBlur = () => {
    setSearchFocused(false);
    Animated.spring(searchBarWidth, { toValue: 1, useNativeDriver: true, speed: 30 }).start();
  };

  const filteredArticles = ARTICLES.filter((a) => {
    const matchCat = selectedCategory === 'all' || a.category === selectedCategory;
    const q = searchQuery.trim().toLowerCase();
    const matchSearch = !q || a.title.toLowerCase().includes(q) || a.summary.toLowerCase().includes(q);
    return matchCat && matchSearch;
  });

  const hasNoResult = searchQuery.trim().length > 0 && filteredArticles.length === 0;

  const handleArticlePress = (id: string) => router.push(`/knowledge/article/${id}`);
  const handleCategoryPress = (id: string) => {
    setSelectedCategory(id);
    setSearchQuery('');
  };

  return (
    <Screen backgroundColor={theme.backgroundRoot}>
      <ScrollView contentContainerStyle={s.scrollContent} showsVerticalScrollIndicator={false}>

        {/* 顶部 Banner */}
        <LinearGradient
          colors={['#667eea', '#764ba2']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={s.banner}
        >
          <ThemedText variant="h2" color="#fff" style={s.bannerTitle}>知识库</ThemedText>
          <ThemedText variant="body" color="rgba(255,255,255,0.85)" style={s.bannerSubtitle}>
            学习急救知识，守护生命安全
          </ThemedText>
          <View style={s.bannerStats}>
            <BannerStat label="篇文章" value="79" />
            <BannerStat label="个分类" value="5" />
            <BannerStat label="位专家" value="12" />
          </View>
        </LinearGradient>

        {/* 搜索框 */}
        <View style={s.searchSection}>
          <Animated.View
            style={[
              s.searchBar,
              {
                backgroundColor: theme.backgroundDefault,
                borderColor: searchFocused ? theme.primary : theme.borderLight,
                transform: [{ scale: searchBarWidth }],
              },
            ]}
          >
            <FontAwesome6
              name="magnifying-glass"
              size={16}
              color={searchFocused ? theme.primary : theme.textMuted}
            />
            <TextInput
              style={[s.searchInput, { color: theme.textPrimary }]}
              placeholder="搜索文章、关键词..."
              placeholderTextColor={theme.textMuted}
              value={searchQuery}
              onChangeText={setSearchQuery}
              onFocus={onSearchFocus}
              onBlur={onSearchBlur}
              returnKeyType="search"
              accessibilityLabel="搜索知识库"
            />
            {searchQuery.length > 0 && (
              <TouchableOpacity onPress={() => setSearchQuery('')} accessibilityLabel="清除搜索">
                <FontAwesome6 name="circle-xmark" size={16} color={theme.textMuted} />
              </TouchableOpacity>
            )}
          </Animated.View>
        </View>

        {/* 分类横滑 */}
        {!searchQuery && (
          <View style={s.categorySection}>
            <ThemedText variant="h3" color={theme.textPrimary} style={s.sectionTitle}>分类浏览</ThemedText>
            <FlatList
              horizontal
              showsHorizontalScrollIndicator={false}
              data={CATEGORIES}
              keyExtractor={(item) => item.id}
              contentContainerStyle={s.categoryList}
              renderItem={({ item }) => (
                <CategoryCard
                  category={item}
                  isSelected={selectedCategory === item.id}
                  onPress={() => handleCategoryPress(item.id)}
                />
              )}
            />
          </View>
        )}

        {/* 文章列表 */}
        <View style={s.articlesSection}>
          <View style={s.articlesSectionHeader}>
            <ThemedText variant="h3" color={theme.textPrimary} style={s.sectionTitle}>
              {searchQuery ? `"${searchQuery}" 的搜索结果` : selectedCategory === 'all' ? '推荐文章' : CATEGORIES.find(c => c.id === selectedCategory)?.name}
            </ThemedText>
            {!searchQuery && (
              <ThemedText variant="caption" color={theme.textMuted}>
                共 {filteredArticles.length} 篇
              </ThemedText>
            )}
          </View>

          {hasNoResult ? (
            <EmptyState
              icon="magnifying-glass"
              title="未找到相关内容"
              subtitle="试试换个关键词，或浏览下方分类"
              actionLabel="清空搜索"
              onActionPress={() => setSearchQuery('')}
            />
          ) : (
            filteredArticles.map((article) => (
              <ArticleCard
                key={article.id}
                article={article}
                onPress={() => handleArticlePress(article.id)}
                theme={theme}
              />
            ))
          )}
        </View>
      </ScrollView>
    </Screen>
  );
}

function BannerStat({ label, value }: { label: string; value: string }) {
  return (
    <View style={s.bannerStatItem}>
      <ThemedText variant="h3" color="#fff" style={s.bannerStatValue}>{value}</ThemedText>
      <ThemedText variant="caption" color="rgba(255,255,255,0.75)" style={s.bannerStatLabel}>{label}</ThemedText>
    </View>
  );
}

function CategoryCard({
  category,
  isSelected,
  onPress,
}: {
  category: Category;
  isSelected: boolean;
  onPress: () => void;
}) {
  const scale = useRef(new Animated.Value(1)).current;
  const onPressIn = () => Animated.spring(scale, { toValue: 0.93, useNativeDriver: true, speed: 50 }).start();
  const onPressOut = () => Animated.spring(scale, { toValue: 1, useNativeDriver: true, speed: 30 }).start();

  return (
    <Animated.View style={{ transform: [{ scale }] }}>
      <TouchableOpacity
        onPress={onPress}
        onPressIn={onPressIn}
        onPressOut={onPressOut}
        activeOpacity={1}
        accessibilityRole="button"
        accessibilityLabel={category.name}
        accessibilityState={{ selected: isSelected }}
      >
        {isSelected ? (
          <LinearGradient
            colors={category.gradient}
            style={[s.categoryCard, s.categoryCardSelected]}
          >
            <FontAwesome6 name={category.icon as any} size={22} color="#fff" />
            <ThemedText variant="smallMedium" color="#fff" style={s.categoryName}>{category.name}</ThemedText>
            <ThemedText variant="caption" color="rgba(255,255,255,0.8)" style={s.categoryCount}>{category.articleCount} 篇</ThemedText>
          </LinearGradient>
        ) : (
          <View style={[s.categoryCard, { backgroundColor: '#F5F5F5' }]}>
            <FontAwesome6 name={category.icon as any} size={22} color={category.gradient[0]} />
            <ThemedText variant="smallMedium" color="#333" style={s.categoryName}>{category.name}</ThemedText>
            <ThemedText variant="caption" color="#888" style={s.categoryCount}>{category.articleCount} 篇</ThemedText>
          </View>
        )}
      </TouchableOpacity>
    </Animated.View>
  );
}

function ArticleCard({
  article,
  onPress,
  theme,
}: {
  article: Article;
  onPress: () => void;
  theme: CreateStylesTheme;
}) {
  const { scale, pressHandlers } = usePressScale(0.97);

  return (
    <Animated.View style={{ transform: [{ scale }], marginBottom: spacing.md }}>
      <TouchableOpacity
        onPress={onPress}
        onPressIn={pressHandlers.onPressIn}
        onPressOut={pressHandlers.onPressOut}
        activeOpacity={1}
        accessibilityRole="button"
        accessibilityLabel={article.title}
        style={[s.articleCard, { backgroundColor: theme.backgroundDefault }]}
      >
        {/* 左侧颜色条 */}
        <View style={[s.articleColorBar, { backgroundColor: article.tagColor }]} />

        <View style={s.articleBody}>
          <View style={s.articleTopRow}>
            <View style={[s.articleTag, { backgroundColor: article.tagColor + '18' }]}>
              <ThemedText variant="caption" color={article.tagColor} style={s.articleTagText}>
                {article.categoryName}
              </ThemedText>
            </View>
            {article.isHot && (
              <View style={s.hotTag}>
                <FontAwesome6 name="fire" size={10} color="#FF6B35" />
                <ThemedText variant="caption" color="#FF6B35" style={s.hotTagText}>热门</ThemedText>
              </View>
            )}
            <View style={s.readTimeTag}>
              <FontAwesome6 name="clock" size={10} color={theme.textMuted} />
              <ThemedText variant="caption" color={theme.textMuted} style={s.readTimeText}>{article.readTime}</ThemedText>
            </View>
          </View>

          <ThemedText variant="bodyMedium" color={theme.textPrimary} style={s.articleTitle}>
            {article.title}
          </ThemedText>
          <ThemedText variant="small" color={theme.textSecondary} style={s.articleSummary} numberOfLines={2}>
            {article.summary}
          </ThemedText>
        </View>

        <FontAwesome6 name="chevron-right" size={14} color={theme.textMuted} style={s.articleArrow} />
      </TouchableOpacity>
    </Animated.View>
  );
}

const s = StyleSheet.create({
  scrollContent: { paddingBottom: spacing['4xl'] },
  banner: {
    paddingHorizontal: spacing.lg,
    paddingTop: 56,
    paddingBottom: spacing['2xl'],
  },
  bannerTitle: { fontSize: 26, fontWeight: '800', color: '#fff', marginBottom: 4 },
  bannerSubtitle: { fontSize: 14, color: 'rgba(255,255,255,0.85)', marginBottom: spacing.lg },
  bannerStats: {
    flexDirection: 'row',
    gap: spacing.xl,
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xl,
  },
  bannerStatItem: { alignItems: 'center' },
  bannerStatValue: { fontSize: 20, fontWeight: '800', color: '#fff' },
  bannerStatLabel: { fontSize: 11, color: 'rgba(255,255,255,0.75)' },

  searchSection: {
    paddingHorizontal: spacing.lg,
    marginTop: spacing.lg,
    marginBottom: spacing.lg,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    paddingHorizontal: spacing.lg,
    height: 48,
    borderRadius: borderRadius.xl,
    borderWidth: 1.5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  searchInput: { flex: 1, fontSize: 15, paddingVertical: 0 },

  categorySection: { marginBottom: spacing.xl },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '700',
    marginBottom: spacing.md,
    paddingHorizontal: spacing.lg,
  },
  categoryList: { paddingHorizontal: spacing.lg, gap: spacing.md },
  categoryCard: {
    width: 100,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
    borderRadius: borderRadius.xl,
    alignItems: 'center',
    gap: 4,
  },
  categoryCardSelected: {
    shadowColor: '#667eea',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 10,
    elevation: 6,
  },
  categoryName: { fontSize: 12, fontWeight: '600', textAlign: 'center' },
  categoryCount: { fontSize: 11 },

  articlesSection: { paddingHorizontal: spacing.lg },
  articlesSectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
    paddingHorizontal: 0,
  },
  articleCard: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: borderRadius.xl,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.07,
    shadowRadius: 8,
    elevation: 2,
  },
  articleColorBar: {
    width: 4,
    alignSelf: 'stretch',
  },
  articleBody: {
    flex: 1,
    padding: spacing.lg,
    gap: spacing.xs,
  },
  articleTopRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: 2,
  },
  articleTag: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 100,
  },
  articleTagText: { fontSize: 11, fontWeight: '600' },
  hotTag: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 3,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 100,
    backgroundColor: '#FF6B3520',
  },
  hotTagText: { fontSize: 10, fontWeight: '700' },
  readTimeTag: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 3,
    marginLeft: 'auto',
  },
  readTimeText: { fontSize: 11 },
  articleTitle: { fontSize: 15, fontWeight: '700', lineHeight: 20 },
  articleSummary: { fontSize: 13, lineHeight: 18, opacity: 0.85 },
  articleArrow: { marginRight: spacing.lg },
});
