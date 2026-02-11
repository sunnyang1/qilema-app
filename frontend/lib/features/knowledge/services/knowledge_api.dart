import 'package:qilema_app/core/network/api_client.dart';
import 'package:qilema_app/core/utils/logger.dart';

/// 知识分类
class KnowledgeCategory {
  final String id;
  final String name;
  final String icon;
  final String description;
  final int articleCount;
  final String color;

  KnowledgeCategory({
    required this.id,
    required this.name,
    required this.icon,
    required this.description,
    required this.articleCount,
    required this.color,
  });

  factory KnowledgeCategory.fromJson(Map<String, dynamic> json) {
    return KnowledgeCategory(
      id: json['id'] as String,
      name: json['name'] as String,
      icon: json['icon'] as String,
      description: json['description'] as String,
      articleCount: json['article_count'] as int,
      color: json['color'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'icon': icon,
      'description': description,
      'article_count': articleCount,
      'color': color,
    };
  }
}

/// 知识文章
class KnowledgeArticle {
  final String id;
  final String title;
  final String summary;
  final String? coverImage;
  final String categoryId;
  final String categoryName;
  final int readCount;
  final DateTime publishTime;
  final int estimatedReadTime;
  final bool isRecommended;

  KnowledgeArticle({
    required this.id,
    required this.title,
    required this.summary,
    this.coverImage,
    required this.categoryId,
    required this.categoryName,
    required this.readCount,
    required this.publishTime,
    required this.estimatedReadTime,
    this.isRecommended = false,
  });

  factory KnowledgeArticle.fromJson(Map<String, dynamic> json) {
    return KnowledgeArticle(
      id: json['id'] as String,
      title: json['title'] as String,
      summary: json['summary'] as String,
      coverImage: json['cover_image'] as String?,
      categoryId: json['category_id'] as String,
      categoryName: json['category_name'] as String,
      readCount: json['read_count'] as int,
      publishTime: DateTime.parse(json['publish_time'] as String),
      estimatedReadTime: json['estimated_read_time'] as int,
      isRecommended: json['is_recommended'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'summary': summary,
      'cover_image': coverImage,
      'category_id': categoryId,
      'category_name': categoryName,
      'read_count': readCount,
      'publish_time': publishTime.toIso8601String(),
      'estimated_read_time': estimatedReadTime,
      'is_recommended': isRecommended,
    };
  }
}

/// 文章内容
class ArticleContent {
  final String id;
  final String title;
  final String? coverImage;
  final String content;
  final String categoryId;
  final String categoryName;
  final int readCount;
  final DateTime publishTime;
  final List<ArticleStep> steps;
  final List<String> tags;
  final int estimatedReadTime;
  final String? summary;

  ArticleContent({
    required this.id,
    required this.title,
    this.coverImage,
    required this.content,
    required this.categoryId,
    required this.categoryName,
    required this.readCount,
    required this.publishTime,
    this.steps = const [],
    this.tags = const [],
    this.estimatedReadTime = 5,
    this.summary,
  });

  factory ArticleContent.fromJson(Map<String, dynamic> json) {
    return ArticleContent(
      id: json['id'] as String,
      title: json['title'] as String,
      coverImage: json['cover_image'] as String?,
      content: json['content'] as String,
      categoryId: json['category_id'] as String,
      categoryName: json['category_name'] as String,
      readCount: json['read_count'] as int,
      publishTime: DateTime.parse(json['publish_time'] as String),
      steps: (json['steps'] as List<dynamic>?)
              ?.map((e) => ArticleStep.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      tags: (json['tags'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      estimatedReadTime: json['estimated_read_time'] as int? ?? 5,
      summary: json['summary'] as String?,
    );
  }
}

/// 文章步骤
class ArticleStep {
  final int order;
  final String title;
  final String content;
  final String? imageUrl;

  ArticleStep({
    required this.order,
    required this.title,
    required this.content,
    this.imageUrl,
  });

  factory ArticleStep.fromJson(Map<String, dynamic> json) {
    return ArticleStep(
      order: json['order'] as int,
      title: json['title'] as String,
      content: json['content'] as String,
      imageUrl: json['image_url'] as String?,
    );
  }
}

/// 急救知识库API服务
class KnowledgeApi {
  static const String _baseUrl = '/api/v1/knowledge';

  /// 获取知识分类列表
  static Future<List<KnowledgeCategory>> getCategories() async {
    try {
      final response = await ApiClient().get('$_baseUrl/categories');

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data['data'] ?? [];
        return data.map((json) => KnowledgeCategory.fromJson(json)).toList();
      }
      return _getMockCategories();
    } catch (e) {
      Logger.e('获取知识分类失败', error: e);
      return _getMockCategories();
    }
  }

  /// 获取文章列表
  static Future<List<KnowledgeArticle>> getArticles({
    String? categoryId,
    String? keyword,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };
      if (categoryId != null) queryParams['category_id'] = categoryId;
      if (keyword != null) queryParams['keyword'] = keyword;

      final response = await ApiClient().get(
        '$_baseUrl/articles',
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data['data'] ?? [];
        return data.map((json) => KnowledgeArticle.fromJson(json)).toList();
      }
      return _getMockArticles(categoryId);
    } catch (e) {
      Logger.e('获取文章列表失败', error: e);
      return _getMockArticles(categoryId);
    }
  }

  /// 获取文章详情
  static Future<ArticleContent?> getArticleDetail(String articleId) async {
    try {
      final response = await ApiClient().get('$_baseUrl/articles/$articleId');

      if (response.statusCode == 200) {
        return ArticleContent.fromJson(response.data['data']);
      }
      return _getMockArticleDetail(articleId);
    } catch (e) {
      Logger.e('获取文章详情失败', error: e);
      return _getMockArticleDetail(articleId);
    }
  }

  /// 搜索文章
  static Future<List<KnowledgeArticle>> searchArticles(String keyword) async {
    return getArticles(keyword: keyword);
  }

  /// 获取推荐文章
  static Future<List<KnowledgeArticle>> getRecommendedArticles() async {
    try {
      final response = await ApiClient().get('$_baseUrl/articles/recommended');

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data['data'] ?? [];
        return data.map((json) => KnowledgeArticle.fromJson(json)).toList();
      }
      return _getMockArticles(null);
    } catch (e) {
      Logger.e('获取推荐文章失败', error: e);
      return _getMockArticles(null);
    }
  }

  /// 模拟分类数据
  static List<KnowledgeCategory> _getMockCategories() {
    return [
      KnowledgeCategory(
        id: 'cpr',
        name: '心肺复苏',
        icon: 'favorite',
        description: 'CPR操作步骤、注意事项和实战技巧',
        articleCount: 12,
        color: '#FF5252',
      ),
      KnowledgeCategory(
        id: 'aed',
        name: 'AED使用',
        icon: 'electric_bolt',
        description: '自动体外除颤器的正确使用方法',
        articleCount: 8,
        color: '#FF9800',
      ),
      KnowledgeCategory(
        id: 'bleeding',
        name: '止血包扎',
        icon: 'healing',
        description: '各类创伤出血的止血和包扎技术',
        articleCount: 15,
        color: '#E91E63',
      ),
      KnowledgeCategory(
        id: 'fracture',
        name: '骨折固定',
        icon: 'straighten',
        description: '骨折识别、固定方法和搬运技巧',
        articleCount: 10,
        color: '#9C27B0',
      ),
      KnowledgeCategory(
        id: 'burn',
        name: '烧伤处理',
        icon: 'local_fire_department',
        description: '不同程度烧伤的急救处理方法',
        articleCount: 6,
        color: '#FF5722',
      ),
      KnowledgeCategory(
        id: 'choking',
        name: '窒息急救',
        icon: 'air',
        description: '海姆立克法等窒息急救技术',
        articleCount: 5,
        color: '#2196F3',
      ),
      KnowledgeCategory(
        id: 'stroke',
        name: '中风识别',
        icon: 'psychology',
        description: '快速识别中风症状和急救措施',
        articleCount: 7,
        color: '#3F51B5',
      ),
      KnowledgeCategory(
        id: 'allergy',
        name: '过敏反应',
        icon: 'coronavirus',
        description: '严重过敏反应的识别和处理',
        articleCount: 4,
        color: '#4CAF50',
      ),
    ];
  }

  /// 模拟文章列表
  static List<KnowledgeArticle> _getMockArticles(String? categoryId) {
    final allArticles = [
      KnowledgeArticle(
        id: 'art_001',
        title: '心肺复苏(CPR)完整操作指南',
        summary: '详细讲解成人心肺复苏的正确操作步骤，包括胸外按压、人工呼吸的比例和技巧，以及AED的配合使用。',
        categoryId: 'cpr',
        categoryName: '心肺复苏',
        readCount: 12580,
        publishTime: DateTime(2026, 1, 15),
        estimatedReadTime: 8,
        isRecommended: true,
      ),
      KnowledgeArticle(
        id: 'art_002',
        title: 'AED自动体外除颤器使用教程',
        summary: '手把手教你使用AED设备，从开机到完成电击的全过程操作，让非专业人员也能在关键时刻挽救生命。',
        categoryId: 'aed',
        categoryName: 'AED使用',
        readCount: 8920,
        publishTime: DateTime(2026, 1, 12),
        estimatedReadTime: 5,
        isRecommended: true,
      ),
      KnowledgeArticle(
        id: 'art_003',
        title: '动脉出血的紧急止血方法',
        summary: '动脉出血危险性极高，学习正确的指压止血法、加压包扎法和止血带使用方法至关重要。',
        categoryId: 'bleeding',
        categoryName: '止血包扎',
        readCount: 7650,
        publishTime: DateTime(2026, 1, 10),
        estimatedReadTime: 6,
        isRecommended: true,
      ),
      KnowledgeArticle(
        id: 'art_004',
        title: '骨折固定的五大原则',
        summary: '骨折现场固定的目的是减轻疼痛、防止进一步损伤。本文介绍骨折固定的基本原则和常用方法。',
        categoryId: 'fracture',
        categoryName: '骨折固定',
        readCount: 5430,
        publishTime: DateTime(2026, 1, 8),
        estimatedReadTime: 7,
      ),
      KnowledgeArticle(
        id: 'art_005',
        title: '烧伤急救"冲脱泡盖送"五步法',
        summary: '烧伤急救的黄金时间是伤后1小时内。掌握"冲、脱、泡、盖、送"五字口诀，正确处理烧伤创面。',
        categoryId: 'burn',
        categoryName: '烧伤处理',
        readCount: 9210,
        publishTime: DateTime(2026, 1, 5),
        estimatedReadTime: 4,
        isRecommended: true,
      ),
      KnowledgeArticle(
        id: 'art_006',
        title: '海姆立克急救法：成人版与婴儿版',
        summary: '气道异物梗阻是常见急症，海姆立克法是最有效的急救方法。本文区分成人和婴儿的不同操作手法。',
        categoryId: 'choking',
        categoryName: '窒息急救',
        readCount: 15670,
        publishTime: DateTime(2026, 1, 3),
        estimatedReadTime: 6,
        isRecommended: true,
      ),
      KnowledgeArticle(
        id: 'art_007',
        title: 'FAST原则：快速识别脑中风',
        summary: 'Face（面部）、Arm（手臂）、Speech（言语）、Time（时间）——掌握FAST原则，快速识别中风症状。',
        categoryId: 'stroke',
        categoryName: '中风识别',
        readCount: 6780,
        publishTime: DateTime(2025, 12, 28),
        estimatedReadTime: 5,
      ),
      KnowledgeArticle(
        id: 'art_008',
        title: '过敏性休克的紧急处理',
        summary: '过敏性休克可在数分钟内危及生命。了解症状识别、肾上腺素使用和后续处理步骤。',
        categoryId: 'allergy',
        categoryName: '过敏反应',
        readCount: 4320,
        publishTime: DateTime(2025, 12, 25),
        estimatedReadTime: 6,
      ),
      KnowledgeArticle(
        id: 'art_009',
        title: '儿童心肺复苏的特殊要点',
        summary: '儿童CPR与成人有所不同，本文讲解1-8岁儿童心肺复苏的比例、深度和技术要点。',
        categoryId: 'cpr',
        categoryName: '心肺复苏',
        readCount: 3890,
        publishTime: DateTime(2025, 12, 20),
        estimatedReadTime: 7,
      ),
      KnowledgeArticle(
        id: 'art_010',
        title: '创伤包扎：绷带与三角巾的使用',
        summary: '掌握绷带包扎法和三角巾使用技巧，可以应对大多数日常创伤的止血和固定需求。',
        categoryId: 'bleeding',
        categoryName: '止血包扎',
        readCount: 5210,
        publishTime: DateTime(2025, 12, 18),
        estimatedReadTime: 8,
      ),
    ];

    if (categoryId == null) {
      return allArticles;
    }

    return allArticles.where((a) => a.categoryId == categoryId).toList();
  }

  /// 模拟文章详情
  static ArticleContent _getMockArticleDetail(String articleId) {
    final articles = {
      'art_001': ArticleContent(
        id: 'art_001',
        title: '心肺复苏(CPR)完整操作指南',
        content: '''
心肺复苏（CPR）是在心跳呼吸骤停时采取的紧急救护措施，是挽救生命的关键技术。

## 操作前准备

1. 确认环境安全
2. 判断意识和呼吸
3. 呼救并拨打120
4. 准备AED设备

## 胸外按压

按压位置：两乳头连线中点
按压深度：5-6厘米
按压频率：100-120次/分钟
按压与放松时间相等

## 人工呼吸

打开气道：仰头抬颏法
吹气时间：每次1秒
观察胸廓：确认有起伏
按压与通气比：30:2
        ''',
        categoryId: 'cpr',
        categoryName: '心肺复苏',
        readCount: 12580,
        publishTime: DateTime(2026, 1, 15),
        steps: [
          ArticleStep(
            order: 1,
            title: '确认环境安全',
            content: '确保现场环境对自己和患者都是安全的，避免二次伤害。',
          ),
          ArticleStep(
            order: 2,
            title: '判断意识和呼吸',
            content: '轻拍患者双肩，大声呼喊。观察胸腹部是否有起伏，判断时间不超过10秒。',
          ),
          ArticleStep(
            order: 3,
            title: '呼救并拨打120',
            content: '如果患者无意识无呼吸，立即让旁人拨打120并取AED。如独自一人，先拨打120并开免提。',
          ),
          ArticleStep(
            order: 4,
            title: '开始胸外按压',
            content: '双手重叠，掌根放在两乳头连线中点，手臂垂直，用上半身力量按压。深度5-6厘米，频率100-120次/分。',
          ),
          ArticleStep(
            order: 5,
            title: '开放气道人工呼吸',
            content: '按压30次后，仰头抬颏开放气道，捏住鼻子，口对口吹气2次，每次1秒，观察胸廓起伏。',
          ),
          ArticleStep(
            order: 6,
            title: '持续循环直到救援到达',
            content: '按30:2的比例持续进行，直到AED到达、专业救援接手或患者恢复呼吸。',
          ),
        ],
        tags: ['心肺复苏', 'CPR', '急救', '胸外按压', '人工呼吸'],
      ),
      'art_002': ArticleContent(
        id: 'art_002',
        title: 'AED自动体外除颤器使用教程',
        content: '''
AED（自动体外除颤器）是一种便携式医疗设备，可以自动分析心律并在需要时给予电击。

## 使用步骤

1. 开机：按下电源按钮
2. 贴电极片：按照图示贴在患者胸部
3. 分析心律：让所有人不要接触患者
4. 电击：如果建议电击，确保无人接触后按下电击按钮
5. 继续CPR：电击后立即继续心肺复苏

## 注意事项

- 电极片要贴紧皮肤
- 分析心律时不要触碰患者
- 电击前大声提醒"所有人离开"
- 如果患者胸部潮湿，先擦干
- 患者有胸毛可能影响贴合，需要剃除
        ''',
        categoryId: 'aed',
        categoryName: 'AED使用',
        readCount: 8920,
        publishTime: DateTime(2026, 1, 12),
        steps: [
          ArticleStep(
            order: 1,
            title: '开启AED',
            content: '打开AED盖子或按下电源按钮，按照语音提示操作。',
          ),
          ArticleStep(
            order: 2,
            title: '贴电极片',
            content: '按照电极片上的图示，一片贴在右锁骨下方，另一片贴在左乳头外侧。',
          ),
          ArticleStep(
            order: 3,
            title: '连接电极片',
            content: '将电极片插头连接到AED主机，等待设备分析心律。',
          ),
          ArticleStep(
            order: 4,
            title: '分析心律',
            content: '大声提醒"所有人离开"，不要触碰患者，让AED分析心律。',
          ),
          ArticleStep(
            order: 5,
            title: '实施电击',
            content: '如果AED建议电击，再次确认无人接触患者，按下闪烁的电击按钮。',
          ),
        ],
        tags: ['AED', '除颤器', '心脏骤停', '电击', '急救设备'],
      ),
    };

    return articles[articleId] ?? ArticleContent(
      id: articleId,
      title: '文章详情',
      content: '文章内容加载中...',
      categoryId: 'other',
      categoryName: '其他',
      readCount: 0,
      publishTime: DateTime.now(),
    );
  }
}
