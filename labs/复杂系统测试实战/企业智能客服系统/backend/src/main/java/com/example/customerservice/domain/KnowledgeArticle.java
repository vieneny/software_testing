package com.example.customerservice.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

@Entity
@Table(name = "knowledge_articles", indexes = {
        @Index(name = "idx_knowledge_tenant_category", columnList = "tenantId,category")
})
public class KnowledgeArticle extends AuditableEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long tenantId;

    @Column(nullable = false, length = 180)
    private String title;

    @Column(nullable = false, length = 80)
    private String category;

    @Lob
    @Column(nullable = false)
    private String content;

    @Column(nullable = false)
    private boolean published = true;

    protected KnowledgeArticle() {
    }

    public KnowledgeArticle(Long tenantId, String title, String category, String content) {
        this.tenantId = tenantId;
        this.title = title;
        this.category = category;
        this.content = content;
    }

    public Long getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getCategory() {
        return category;
    }

    public String getContent() {
        return content;
    }
}
