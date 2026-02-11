import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:qilema_app/features/knowledge/providers/knowledge_provider.dart';
import 'package:qilema_app/features/knowledge/services/knowledge_api.dart';

/// 文章列表页面
class ArticlesPage extends ConsumerStatefulWidget {
  final String? categoryId;

  const ArticlesPage({super.key, this.categoryId});

  @override
  ConsumerState<ArticlesPage> createState() => _ArticlesPageState();
}

class _ArticlesPageState extends ConsumerState<ArticlesPage> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    
    Future.microtask(() {
      if (widget.categoryId != null) {
        ref.read(knowledgeProvider.notifier).selectCategory(widget.categoryId);
      } else {
        ref.read(knowledgeProvider.notifier).loadArticles(refresh: true);
      }
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      ref.read(knowledgeProvider.notifier).loadMore();
    }
  }

  String _getPageTitle(KnowledgeState state) {
    if (widget.categoryId != null && state.categories.isNotEmpty) {
      final category = state.categories.firstWhere(
        (c) => c.id == widget.categoryId,
        orElse: () => KnowledgeCategory(
          id: '',
          name: '文章列表',
          icon: '',
          description: '',
          articleCount: 0,
          color: '',
        ),
      );
      return category.name;
    }
    return '文章列表';
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(knowledgeProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(_getPageTitle(state)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/knowledge'),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(knowledgeProvider.notifier).loadArticles(refresh: true),
        child: _buildBody(state),
      ),
    );
  }

  Widget _buildBody(KnowledgeState state) {
    if (state.isLoadingArticles && state.articles.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state.articlesState == LoadingState.error && state.articles.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              state.errorMessage ?? '加载失败',
              style: TextStyle(color: Colors.grey.shade600),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => ref.read(knowledgeProvider.notifier).loadArticles(refresh: true),
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    if (state.articles.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.article_outlined,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              '暂无文章',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: state.articles.length + (state.hasMore ? 1 : 0),
      itemBuilder: (context, index) {
        if (index >= state.articles.length) {
          return const Center(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: CircularProgressIndicator(),
            ),
          );
        }

        final article = state.articles[index];
        return _ArticleCard(article: article);
      },
    );
  }
}

/// 文章卡片
class _ArticleCard extends StatelessWidget {
  final KnowledgeArticle article;

  const _ArticleCard({required this.article});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          context.go('/knowledge/articles/${article.id}');
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (article.isRecommended)
                Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.star, size: 12, color: Colors.red.shade600),
                      const SizedBox(width: 2),
                      Text(
                        '推荐',
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.red.shade600,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              Text(
                article.title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              Text(
                article.summary,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      article.categoryName,
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.blue.shade700,
                      ),
                    ),
                  ),
                  const Spacer(),
                  Icon(Icons.access_time, size: 14, color: Colors.grey.shade500),
                  const SizedBox(width: 2),
                  Text(
                    '${article.estimatedReadTime}分钟',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade500,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Icon(Icons.remove_red_eye, size: 14, color: Colors.grey.shade500),
                  const SizedBox(width: 2),
                  Text(
                    _formatReadCount(article.readCount),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade500,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatReadCount(int count) {
    if (count >= 10000) {
      return '${(count / 10000).toStringAsFixed(1)}万';
    } else if (count >= 1000) {
      return '${(count / 1000).toStringAsFixed(1)}k';
    }
    return count.toString();
  }
}
