package com.example.customerservice.repository;

import com.example.customerservice.domain.AgentAssignment;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AgentAssignmentRepository extends JpaRepository<AgentAssignment, Long> {

    long countByTicketId(Long ticketId);
}
