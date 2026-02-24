import React, { useState } from 'react';
import { View, ScrollView, TextInput, TouchableOpacity, StyleSheet, FlatList } from 'react-native';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { FontAwesome6 } from '@expo/vector-icons';
import { useTheme } from '@/hooks/useTheme';
import { Spacing, BorderRadius } from '@/constants/theme-warm';
import { useSafeRouter } from '@/hooks/useSafeRouter';

interface Category {
  id: string;
  name: string;
  icon: string;
  articleCount: number;
  color: string;
}

interface Article {
  id: string;
  title: string;
  summary: string;
  category: string;
  readTime: string;
}

export default function KnowledgeScreen() {
  const { theme, isDark } = useTheme();
  const router = useSafeRouter();
  const [searchQuery, setSearchQuery] = useState('');

  const categories: Category[] = [
    { id: 'emergency', name: '急救知识', icon: 'truck-medical', articleCount: 12, color: theme.error },
    { id: 'health', name: '健康常识', icon: 'heart-pulse', articleCount: 24, color: theme.accent },
    { id: 'chronic', name: '慢性病', icon: 'lungs', articleCount: 18, color: theme.primary },
    { id: 'elderly', name: '老年人护理', icon: 'person-cane', articleCount: 15, color: theme.warning },
    { id: 'prevention', name: '疾病预防', icon: 'shield-heart', articleCount: 20, color: theme.info },
  ];

  const popularArticles: Article[] = [
    {
      id: '1',
      title: '心肺复苏（CPR）步骤详解',
      summary: '掌握正确的心肺复苏方法，关键时刻能救命',
      category: 'emergency',
      readTime: '5分钟',
    },
    {
      id: '2',
      title: '高血压患者的日常注意事项',
      summary: '科学管理血压，预防并发症',
      category: 'chronic',
      readTime: '8分钟',
    },
    {
      id: '3',
      title: '独居老人安全指南',
      summary: '全面保障独居老人的安全',
      category: 'elderly',
      readTime: '10分钟',
    },
    {
      id: '4',
      title: '常见急救药物使用指南',
      summary: '正确使用急救药物，避免误用',
      category: 'emergency',
      readTime: '6分钟',
    },
  ];

  const handleCategoryPress = (categoryId: string) => {
    router.push(`/knowledge/category/${categoryId}`);
  };

  const handleArticlePress = (articleId: string) => {
    router.push(`/knowledge/article/${articleId}`);
  };

  const renderCategory = ({ item }: { item: Category }) => (
    <TouchableOpacity
      style={[styles.categoryCard, { backgroundColor: theme.backgroundDefault }]}
      onPress={() => handleCategoryPress(item.id)}
      activeOpacity={0.7}
    >
      <View style={[styles.categoryIcon, { backgroundColor: `${item.color}15` }]}>
        <FontAwesome6 name={item.icon as any} size={24} color={item.color} />
      </View>
      <ThemedText variant="bodyMedium" color={theme.textPrimary} style={styles.categoryName}>
        {item.name}
      </ThemedText>
      <ThemedText variant="caption" color={theme.textMuted}>
        {item.articleCount} 篇文章
      </ThemedText>
    </TouchableOpacity>
  );

  const renderArticle = ({ item }: { item: Article }) => (
    <TouchableOpacity
      style={[styles.articleCard, { backgroundColor: theme.backgroundDefault }]}
      onPress={() => handleArticlePress(item.id)}
      activeOpacity={0.7}
    >
      <View style={styles.articleHeader}>
        <ThemedText variant="title" color={theme.textPrimary} style={styles.articleTitle}>
          {item.title}
        </ThemedText>
        <View style={styles.articleMeta}>
          <FontAwesome6 name="clock" size={12} color={theme.textMuted} />
          <ThemedText variant="caption" color={theme.textMuted} style={styles.metaText}>
            {item.readTime}
          </ThemedText>
        </View>
      </View>
      <ThemedText variant="small" color={theme.textSecondary} style={styles.articleSummary}>
        {item.summary}
      </ThemedText>
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <ThemedText variant="h1" color={theme.textPrimary}>
          知识库
        </ThemedText>
        <ThemedText variant="body" color={theme.textSecondary}>
          学习急救知识，守护生命安全
        </ThemedText>
      </View>

      <View style={styles.searchContainer}>
        <FontAwesome6 name="magnifying-glass" size={20} color={theme.textMuted} style={styles.searchIcon} />
        <TextInput
          style={[styles.searchInput, { color: theme.textPrimary, backgroundColor: theme.backgroundTertiary }]}
          placeholder="搜索文章..."
          placeholderTextColor={theme.textMuted}
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
      </View>

      <View style={styles.section}>
        <ThemedText variant="h3" color={theme.textPrimary} style={styles.sectionTitle}>
          分类浏览
        </ThemedText>
        <FlatList
          data={categories}
          renderItem={renderCategory}
          keyExtractor={(item) => item.id}
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoryList}
        />
      </View>

      <View style={styles.section}>
        <ThemedText variant="h3" color={theme.textPrimary} style={styles.sectionTitle}>
          热门文章
        </ThemedText>
        {popularArticles.map((article) => (
          <ArticleItem key={article.id} article={article} onPress={() => handleArticlePress(article.id)} />
        ))}
      </View>
    </ScrollView>
  );
}

function ArticleItem({ article, onPress }: { article: Article; onPress: () => void }) {
  const { theme } = useTheme();
  return (
    <TouchableOpacity
      style={[styles.articleCard, { backgroundColor: theme.backgroundDefault }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.articleHeader}>
        <ThemedText variant="title" color={theme.textPrimary} style={styles.articleTitle}>
          {article.title}
        </ThemedText>
        <View style={styles.articleMeta}>
          <FontAwesome6 name="clock" size={12} color={theme.textMuted} />
          <ThemedText variant="caption" color={theme.textMuted} style={styles.metaText}>
            {article.readTime}
          </ThemedText>
        </View>
      </View>
      <ThemedText variant="small" color={theme.textSecondary} style={styles.articleSummary}>
        {article.summary}
      </ThemedText>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAFAFA',
  },
  header: {
    padding: Spacing['2xl'],
    paddingBottom: Spacing.xl,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: Spacing['2xl'],
    marginBottom: Spacing.xl,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    borderRadius: BorderRadius.lg,
  },
  searchIcon: {
    marginRight: Spacing.md,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    paddingVertical: 4,
  },
  section: {
    paddingHorizontal: Spacing['2xl'],
    marginBottom: Spacing['2xl'],
  },
  sectionTitle: {
    marginBottom: Spacing.lg,
  },
  categoryList: {
    gap: Spacing.md,
  },
  categoryCard: {
    width: 120,
    padding: Spacing.lg,
    borderRadius: BorderRadius.lg,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  categoryIcon: {
    width: 56,
    height: 56,
    borderRadius: BorderRadius.md,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  categoryName: {
    textAlign: 'center',
    marginBottom: Spacing.xs,
  },
  articleCard: {
    padding: Spacing.lg,
    borderRadius: BorderRadius.lg,
    marginBottom: Spacing.lg,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  articleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: Spacing.sm,
  },
  articleTitle: {
    flex: 1,
    marginRight: Spacing.md,
  },
  articleMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  metaText: {
    marginLeft: 4,
  },
  articleSummary: {
    lineHeight: 20,
  },
});
