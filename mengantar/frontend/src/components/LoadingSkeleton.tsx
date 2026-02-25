"use client";

export default function LoadingSkeleton() {
    return (
        <div className="loading-skeleton">
            <div className="skeleton-avatar" />
            <div className="skeleton-content">
                <div className="skeleton-line short" />
                <div className="skeleton-line long" />
            </div>
        </div>
    );
}
