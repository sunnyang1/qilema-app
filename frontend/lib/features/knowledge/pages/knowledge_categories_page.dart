import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:qilema_app/features/knowledge/providers/knowledge_provider.dart';
import 'package:qilema_app/features/knowledge/services/knowledge_api.dart';

/// 急救知识分类页面
class KnowledgeCategoriesPage extends ConsumerStatefulWidget {
  const KnowledgeCategoriesPage({super.key});

  @override
  ConsumerState<KnowledgeCategoriesPage> createState() => _KnowledgeCategoriesPageState();
}

class _KnowledgeCategoriesPageState extends ConsumerState<KnowledgeCategoriesPage> {
  @override
  void initState() {
    super.initState();
    // 延迟加载，等待widget构建完成
    Future.microtask(() {
      ref.read(knowledgeProvider.notifier).loadCategories();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(knowledgeProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('急救知识库'),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              context.go('/knowledge/search');
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(knowledgeProvider.notifier).loadCategories(),
        child: _buildBody(state),
      ),
    );
  }

  Widget _buildBody(KnowledgeState state) {
    if (state.isLoadingCategories && state.categories.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state.categoriesState == LoadingState.error && state.categories.isEmpty) {
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
              onPressed: () => ref.read(knowledgeProvider.notifier).loadCategories(),
              child: const Text('重试'),
            ),
          ],
        ),
      );
    }

    if (state.categories.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.folder_open,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            Text(
              '暂无知识分类',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // 推荐文章区域
        _buildRecommendedSection(),
        const SizedBox(height: 24),
        // 分类标题
        const Text(
          '知识分类',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        // 分类网格
        _buildCategoriesGrid(state.categories),
      ],
    );
  }

  /// 构建推荐区域
  Widget _buildRecommendedSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.red.shade400, Colors.red.shade600],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.star, color: Colors.white, size: 14),
                    SizedBox(width: 4),
                    Text(
                      '推荐学习',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            '心肺复苏(CPR)完整操作指南',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '掌握心肺复苏技能，关键时刻挽救生命',
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.9),
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 12),
          ElevatedButton(
            onPressed: () {
              context.go('/knowledge/articles/art_001');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: Colors.red.shade600,
            ),
            child: const Text('立即学习'),
          ),
        ],
      ),
    );
  }

  /// 构成分类网格
  Widget _buildCategoriesGrid(List<KnowledgeCategory> categories) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 1.3,
      ),
      itemCount: categories.length,
      itemBuilder: (context, index) {
        final category = categories[index];
        return _CategoryCard(category: category);
      },
    );
  }
}

/// 分类卡片
class _CategoryCard extends StatelessWidget {
  final KnowledgeCategory category;

  const _CategoryCard({required this.category});

  @override
  Widget build(BuildContext context) {
    final color = _getColorFromHex(category.color);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: () {
          context.go('/knowledge/category/${category.id}');
        },
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: color.withValues(alpha: 0.3),
              width: 1,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  _getIconData(category.icon),
                  color: color,
                  size: 28,
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    category.name,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${category.articleCount} 篇文章',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
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

  Color _getColorFromHex(String hex) {
    final hexCode = hex.replaceAll('#', '');
    return Color(int.parse('FF$hexCode', radix: 16));
  }

  IconData _getIconData(String iconName) {
    switch (iconName) {
      case 'favorite':
        return Icons.favorite;
      case 'electric_bolt':
        return Icons.electric_bolt;
      case 'healing':
        return Icons.healing;
      case 'straighten':
        return Icons.straighten;
      case 'local_fire_department':
        return Icons.local_fire_department;
      case 'air':
        return Icons.air;
      case 'psychology':
        return Icons.psychology;
      case 'coronavirus':
        return Icons.coronavirus;
      default:
        return Icons.article;
    }
  }
}
