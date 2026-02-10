import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:qilema_app/features/knowledge/services/knowledge_api.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 加载状态
enum LoadingState { initial, loading, success, error }

/// 急救知识库状态
class KnowledgeState {
  final LoadingState categoriesState;
  final LoadingState articlesState;
  final LoadingState articleDetailState;
  final List<KnowledgeCategory> categories;
  final List<KnowledgeArticle> articles;
  final ArticleContent? currentArticle;
  final String? selectedCategoryId;
  final String? searchKeyword;
  final String? errorMessage;
  final int currentPage;
  final bool hasMore;

  const KnowledgeState({
    this.categoriesState = LoadingState.initial,
    this.articlesState = LoadingState.initial,
    this.articleDetailState = LoadingState.initial,
    this.categories = const [],
    this.articles = const [],
    this.currentArticle,
    this.selectedCategoryId,
    this.searchKeyword,
    this.errorMessage,
    this.currentPage = 1,
    this.hasMore = true,
  });

  KnowledgeState copyWith({
    LoadingState? categoriesState,
    LoadingState? articlesState,
    LoadingState? articleDetailState,
    List<KnowledgeCategory>? categories,
    List<KnowledgeArticle>? articles,
    ArticleContent? currentArticle,
    String? selectedCategoryId,
    String? searchKeyword,
    String? errorMessage,
    int? currentPage,
    bool? hasMore,
  }) {
    return KnowledgeState(
      categoriesState: categoriesState ?? this.categoriesState,
      articlesState: articlesState ?? this.articlesState,
      articleDetailState: articleDetailState ?? this.articleDetailState,
      categories: categories ?? this.categories,
      articles: articles ?? this.articles,
      currentArticle: currentArticle ?? this.currentArticle,
      selectedCategoryId: selectedCategoryId ?? this.selectedCategoryId,
      searchKeyword: searchKeyword ?? this.searchKeyword,
      errorMessage: errorMessage ?? this.errorMessage,
      currentPage: currentPage ?? this.currentPage,
      hasMore: hasMore ?? this.hasMore,
    );
  }

  bool get isLoadingCategories => categoriesState == LoadingState.loading;
  bool get isLoadingArticles => articlesState == LoadingState.loading;
  bool get isLoadingArticleDetail => articleDetailState == LoadingState.loading;
  bool get hasError => categoriesState == LoadingState.error || 
                       articlesState == LoadingState.error ||
                       articleDetailState == LoadingState.error;
}

/// 知识库状态管理
class KnowledgeNotifier extends StateNotifier<KnowledgeState> {
  KnowledgeNotifier() : super(const KnowledgeState());

  /// 加载分类列表
  Future<void> loadCategories() async {
    state = state.copyWith(categoriesState: LoadingState.loading);

    try {
      final categories = await KnowledgeApi.getCategories();
      state = state.copyWith(
        categoriesState: LoadingState.success,
        categories: categories,
        errorMessage: null,
      );
    } catch (e) {
      Logger.e('加载分类失败', error: e);
      state = state.copyWith(
        categoriesState: LoadingState.error,
        errorMessage: '加载分类失败: ${e.toString()}',
      );
    }
  }

  /// 加载文章列表
  Future<void> loadArticles({bool refresh = false}) async {
    if (refresh) {
      state = state.copyWith(
        currentPage: 1,
        hasMore: true,
        articles: [],
      );
    }

    if (!state.hasMore && !refresh) return;

    state = state.copyWith(articlesState: LoadingState.loading);

    try {
      final articles = await KnowledgeApi.getArticles(
        categoryId: state.selectedCategoryId,
        keyword: state.searchKeyword,
        page: state.currentPage,
      );

      final allArticles = refresh 
          ? articles 
          : [...state.articles, ...articles];

      state = state.copyWith(
        articlesState: LoadingState.success,
        articles: allArticles,
        hasMore: articles.length >= 20,
        currentPage: state.currentPage + 1,
        errorMessage: null,
      );
    } catch (e) {
      Logger.e('加载文章失败', error: e);
      state = state.copyWith(
        articlesState: LoadingState.error,
        errorMessage: '加载文章失败: ${e.toString()}',
      );
    }
  }

  /// 选择分类
  Future<void> selectCategory(String? categoryId) async {
    state = state.copyWith(
      selectedCategoryId: categoryId,
      currentPage: 1,
      hasMore: true,
    );
    await loadArticles(refresh: true);
  }

  /// 搜索文章
  Future<void> searchArticles(String keyword) async {
    state = state.copyWith(
      searchKeyword: keyword.isEmpty ? null : keyword,
      currentPage: 1,
      hasMore: true,
    );
    await loadArticles(refresh: true);
  }

  /// 加载文章详情
  Future<void> loadArticleDetail(String articleId) async {
    state = state.copyWith(articleDetailState: LoadingState.loading);

    try {
      final article = await KnowledgeApi.getArticleDetail(articleId);
      if (article != null) {
        state = state.copyWith(
          articleDetailState: LoadingState.success,
          currentArticle: article,
          errorMessage: null,
        );
      } else {
        state = state.copyWith(
          articleDetailState: LoadingState.error,
          errorMessage: '文章不存在',
        );
      }
    } catch (e) {
      Logger.e('加载文章详情失败', error: e);
      state = state.copyWith(
        articleDetailState: LoadingState.error,
        errorMessage: '加载文章详情失败: ${e.toString()}',
      );
    }
  }

  /// 清除当前文章
  void clearCurrentArticle() {
    state = state.copyWith(currentArticle: null);
  }

  /// 清除搜索
  void clearSearch() {
    state = state.copyWith(
      searchKeyword: null,
      currentPage: 1,
      hasMore: true,
    );
  }

  /// 刷新
  Future<void> refresh() async {
    await Future.wait([
      loadCategories(),
      loadArticles(refresh: true),
    ]);
  }

  /// 加载更多
  Future<void> loadMore() async {
    if (!state.isLoadingArticles && state.hasMore) {
      await loadArticles();
    }
  }
}

/// 知识库Provider
final knowledgeProvider = StateNotifierProvider<KnowledgeNotifier, KnowledgeState>((ref) {
  return KnowledgeNotifier();
});
