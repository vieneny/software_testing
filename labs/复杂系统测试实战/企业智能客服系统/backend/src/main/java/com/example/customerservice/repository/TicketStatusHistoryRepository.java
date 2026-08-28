package com.example.customerservice.repository;

import com.example.customerservice.domain.TicketStatusHistory;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TicketStatusHistoryRepository extends JpaRepository<TicketStatusHistory, Long> {

    List<TicketStatusHistory> findByTicketIdOrderByCreatedAtAsc(Long ticketId);
}
