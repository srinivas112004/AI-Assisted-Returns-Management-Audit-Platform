import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'gray';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'gray', size = 'sm' }) => {
  const variantStyles = {
    primary: 'bg-blue-50 text-blue-700 border-blue-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200',
    info: 'bg-sky-50 text-sky-700 border-sky-200',
    gray: 'bg-slate-100 text-slate-700 border-slate-200',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1 font-medium',
  };

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border ${variantStyles[variant]} ${sizeStyles[size]}`}
    >
      {children}
    </span>
  );
};

export const getStatusBadgeVariant = (status: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'gray' => {
  const s = status.toUpperCase();
  if (['COMPLETED', 'DELIVERED', 'ELIGIBLE', 'FULLY_ELIGIBLE', 'PASS', 'SUCCESS', 'RESTOCK'].includes(s)) {
    return 'success';
  }
  if (['AUTHORIZED', 'IN_TRANSIT', 'PARTIALLY_ELIGIBLE', 'PARTIALLY_REFUNDED', 'PASS_WITH_RESTOCKING_FEE', 'REFURBISH'].includes(s)) {
    return 'primary';
  }
  if (['PENDING', 'SUBMITTED', 'PENDING_REVIEW', 'QUARANTINE_REQUIRED', 'QUARANTINE', 'LABEL_CREATED', 'SPLIT'].includes(s)) {
    return 'warning';
  }
  if (['REJECTED', 'INELIGIBLE', 'REJECT_SCRAP', 'SCRAP', 'BLOCKED_DUPLICATE', 'FAIL', 'CANCELLED', 'MISSING'].includes(s)) {
    return 'danger';
  }
  return 'gray';
};

