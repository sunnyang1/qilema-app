import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:qilema_app/features/knowledge/providers/knowledge_provider.dart';
import 'package:qilema_app/features/knowledge/services/knowledge_api.dart';
import 'package:share_plus/share_plus.dart';

/// 文章详情页面
class ArticleDetailPage extends ConsumerStatefulWidget {
  final String articleId;

  const ArticleDetailPage({super.key, required this.articleId});

  @override
  ConsumerState<ArticleDetailPage> createState() => _ArticleDetailPageState();
}

class _ArticleDetailPageState extends ConsumerState<ArticleDetailPage> {
  bool _isBookmarked = false;

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(knowledgeProvider.notifier).loadArticleDetail(widget.articleId);
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(knowledgeProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('文章详情'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/knowledge'),
        ),
        actions: [
          IconButton(
            icon: Icon(_isBookmarked ? Icons.bookmark : Icons.bookmark_border),
            onPressed: () {
              setState(() {
                _isBookmarked = !_isBookmarked;
              });
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(_isBookmarked ? '已收藏' : '已取消收藏'),
                ),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () {
              _shareArticle(state.currentArticle);
            },
          ),
        ],
      ),
      body: _buildBody(state),
    );
  }

  Widget _buildBody(KnowledgeState state) {
    if (state.isLoadingArticleDetail) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state.articleDetailState == LoadingState.error) {
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
              onPressed: () => ref.read(knowledgeProvider.notifier).loadArticleDetail(widget.articleId),
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    final article = state.currentArticle;
    if (article == null) {
      return const Center(child: Text('文章不存在'));
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 分类标签
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              article.categoryName,
              style: TextStyle(
                fontSize: 12,
                color: Colors.blue.shade700,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 12),
          // 标题
          Text(
            article.title,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          // 元信息
          Row(
            children: [
              Icon(Icons.access_time, size: 16, color: Colors.grey.shade500),
              const SizedBox(width: 4),
              Text(
                '${article.estimatedReadTime}分钟阅读',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(width: 16),
              Icon(Icons.remove_red_eye, size: 16, color: Colors.grey.shade500),
              const SizedBox(width: 4),
              Text(
                '${article.readCount} 次阅读',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            '发布时间: ${DateFormat('yyyy-MM-dd').format(article.publishTime)}',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade500,
            ),
          ),
          const Divider(height: 32),
          // 步骤列表（如果有）
          if (article.steps.isNotEmpty) ...[
            const Text(
              '操作步骤',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            ...article.steps.map((step) => _buildStepCard(step)),
            const Divider(height: 32),
          ],
          // 文章内容
          Text(
            article.content,
            style: const TextStyle(
              fontSize: 16,
              height: 1.8,
            ),
          ),
          const SizedBox(height: 24),
          // 标签
          if (article.tags.isNotEmpty) ...[
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: article.tags.map((tag) => Chip(
                label: Text(tag),
                backgroundColor: Colors.grey.shade100,
                labelStyle: TextStyle(
                  color: Colors.grey.shade700,
                  fontSize: 12,
                ),
                padding: EdgeInsets.zero,
                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              )).toList(),
            ),
            const SizedBox(height: 24),
          ],
          // 提示
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.orange.shade50,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.orange.shade200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.info, color: Colors.orange.shade700),
                    const SizedBox(width: 8),
                    Text(
                      '重要提示',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.orange.shade900,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  '本文仅供急救知识学习参考。在实际紧急情况下，请立即拨打120急救电话，并在专业医护人员指导下进行操作。',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.orange.shade800,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStepCard(ArticleStep step) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: Colors.blue.shade600,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Center(
                child: Text(
                  '${step.order}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    step.title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    step.content,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade700,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _shareArticle(ArticleContent? article) {
    if (article == null) return;

    SharePlus.instance.share(
      ShareParams(
        text: '【${article.title}】\n\n${article.summary ?? ""}\n\n来自"起了吗"急救知识库',
        subject: article.title,
      ),
    );
  }
}
