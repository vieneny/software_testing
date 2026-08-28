package com.example.customerservice.repository;

import com.example.customerservice.domain.KnowledgeArticle;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface KnowledgeArticleRepository extends JpaRepository<KnowledgeArticle, Long> {

    List<KnowledgeArticle> findTop5ByTenantIdAndPublishedTrueAndCategoryOrderByUpdatedAtDesc(
            Long tenantId,
            String category
    );
}
