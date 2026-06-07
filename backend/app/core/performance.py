"""
Performance optimization utilities - caching, query optimization, indexing
"""
import logging
from functools import wraps
from typing import Optional, Callable, Any
import hashlib
import json
from datetime import timedelta

logger = logging.getLogger(__name__)


def get_redis_client():
    """Get Redis client for caching"""
    try:
        import redis
        from app.core.config import settings
        return redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return None


def cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a consistent cache key from function arguments
    
    Args:
        prefix: Cache key prefix (e.g., "property", "user", "metrics")
        args: Positional arguments to include in key
        kwargs: Keyword arguments to include in key
    
    Returns:
        Cache key string
    """
    # Create a deterministic string from arguments
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    
    # Hash if the key would be too long
    key_str = ":".join(key_parts)
    if len(key_str) > 200:
        key_str = hashlib.md5(key_str.encode()).hexdigest()
    
    return f"{prefix}:{key_str}"


def cached(prefix: str, ttl_seconds: int = 300):
    """
    Decorator to cache function results in Redis
    
    Args:
        prefix: Cache key prefix
        ttl_seconds: Time to live in seconds (default 5 minutes)
    
    Usage:
        @cached("property_detail", ttl_seconds=600)
        def get_property(property_id: int):
            # Expensive database query
            return property
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            redis_client = get_redis_client()
            
            # If Redis is unavailable, just call the function
            if redis_client is None:
                return func(*args, **kwargs)
            
            # Generate cache key
            key = cache_key(prefix, *args, **kwargs)
            
            try:
                # Try to get from cache
                cached_value = redis_client.get(key)
                if cached_value:
                    logger.debug(f"Cache hit for {key}")
                    return json.loads(cached_value)
                
                # Cache miss - call function
                logger.debug(f"Cache miss for {key}")
                result = func(*args, **kwargs)
                
                # Store in cache
                redis_client.setex(
                    key,
                    ttl_seconds,
                    json.dumps(result, default=str)  # default=str handles datetime, etc.
                )
                
                return result
                
            except Exception as e:
                logger.error(f"Cache error for {key}: {e}")
                # On error, just call the function
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def invalidate_cache(prefix: str, *args, **kwargs):
    """
    Invalidate a cached value
    
    Args:
        prefix: Cache key prefix
        args: Positional arguments used in original cache
        kwargs: Keyword arguments used in original cache
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return
    
    key = cache_key(prefix, *args, **kwargs)
    try:
        redis_client.delete(key)
        logger.debug(f"Invalidated cache for {key}")
    except Exception as e:
        logger.error(f"Error invalidating cache for {key}: {e}")


def invalidate_pattern(pattern: str):
    """
    Invalidate all keys matching a pattern
    
    Args:
        pattern: Redis key pattern (e.g., "property:*", "user:123:*")
    """
    redis_client = get_redis_client()
    if redis_client is None:
        return
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys matching {pattern}")
    except Exception as e:
        logger.error(f"Error invalidating cache pattern {pattern}: {e}")


# Database optimization recommendations
DATABASE_INDEXES = """
-- Performance Optimization: Recommended Database Indexes
-- Run these migrations to improve query performance

-- Users table (authentication and lookups)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id ON users(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON users(subscription_status);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active) WHERE is_active = true;

-- Properties table (main queries)
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_zip_code ON properties(zip_code);
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(list_price);
CREATE INDEX IF NOT EXISTS idx_properties_updated_at ON properties(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_properties_external_id ON properties(external_id);

-- Properties geospatial (map queries)
CREATE INDEX IF NOT EXISTS idx_properties_location ON properties USING GIST(location);

-- Affiliates table
CREATE INDEX IF NOT EXISTS idx_affiliates_user_id ON affiliates(user_id);
CREATE INDEX IF NOT EXISTS idx_affiliates_code ON affiliates(code);
CREATE INDEX IF NOT EXISTS idx_affiliates_status ON affiliates(status);

-- Referral attributions
CREATE INDEX IF NOT EXISTS idx_referral_attr_referred_user ON referral_attributions(referred_user_id);
CREATE INDEX IF NOT EXISTS idx_referral_attr_affiliate ON referral_attributions(affiliate_id);

-- Commission ledger (payout queries)
CREATE INDEX IF NOT EXISTS idx_commission_status ON commission_ledger(status);
CREATE INDEX IF NOT EXISTS idx_commission_affiliate ON commission_ledger(affiliate_id);
CREATE INDEX IF NOT EXISTS idx_commission_hold_until ON commission_ledger(hold_until);
CREATE INDEX IF NOT EXISTS idx_commission_stripe_invoice ON commission_ledger(stripe_invoice_id);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_commission_affiliate_status 
    ON commission_ledger(affiliate_id, status) 
    WHERE fraud_flagged = false;

CREATE INDEX IF NOT EXISTS idx_properties_status_updated 
    ON properties(status, updated_at DESC);

-- Fraud signals
CREATE INDEX IF NOT EXISTS idx_fraud_affiliate ON fraud_signals(affiliate_id);
CREATE INDEX IF NOT EXISTS idx_fraud_referred_user ON fraud_signals(referred_user_id);
CREATE INDEX IF NOT EXISTS idx_fraud_resolved ON fraud_signals(resolved) WHERE resolved = false;
"""


def log_slow_query(func: Callable) -> Callable:
    """
    Decorator to log slow database queries
    
    Usage:
        @log_slow_query
        def expensive_query(db: Session):
            return db.query(Property).all()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        
        if elapsed > 1.0:  # Log queries taking more than 1 second
            logger.warning(f"Slow query in {func.__name__}: {elapsed:.2f}s")
        
        return result
    
    return wrapper


# Query optimization tips
QUERY_OPTIMIZATION_TIPS = """
Performance Optimization Best Practices:

1. USE INDEXES:
   - All WHERE clauses should use indexed columns
   - Foreign keys should have indexes
   - Add composite indexes for common multi-column queries

2. LIMIT RESULTS:
   - Always use .limit() in production queries
   - Paginate large result sets
   - Default limit: 100 items

3. SELECT SPECIFIC COLUMNS:
   - Use .with_entities() to select only needed columns
   - Avoid SELECT * in large tables
   - Load relationships only when needed (avoid N+1 queries)

4. USE EAGER LOADING:
   - Use .joinedload() for one-to-one relationships
   - Use .subqueryload() for one-to-many relationships
   - Prevents N+1 query problems

5. CACHE EXPENSIVE QUERIES:
   - Use @cached decorator for read-heavy operations
   - Invalidate cache on writes
   - Cache API responses, not just DB queries

6. DATABASE CONNECTION POOLING:
   - SQLAlchemy pool is already configured
   - Default: 5 connections min, 20 max
   - Monitor connection usage in production

7. BATCH OPERATIONS:
   - Use bulk_insert_mappings() for multiple inserts
   - Use bulk_update_mappings() for multiple updates
   - Commit in batches, not per-record

Example optimized query:

# BAD - N+1 problem
properties = db.query(Property).all()
for prop in properties:
    print(prop.unit_details)  # Triggers N additional queries!

# GOOD - Eager loading
properties = db.query(Property).options(
    joinedload(Property.unit_details)
).limit(100).all()
"""
