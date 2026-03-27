/**
 * MarketplaceBrowse Page
 * 
 * Browse and search marketplace blocks
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Input, 
  Select, 
  Row, 
  Col, 
  Tag, 
  Button, 
  Typography, 
  Spin,
  Empty,
  Rate,
  Pagination,
  Space,
  Menu,
  Dropdown,
} from 'antd';
import { 
  SearchOutlined, 
  ShopOutlined,
  DownloadOutlined,
  StarOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import { apiFetch } from '@/utils';

const { Title, Text, Paragraph } = Typography;

function MarketplaceBrowse() {
  const [listings, setListings] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [pagination, setPagination] = useState({ page: 1, per_page: 12, total: 0 });

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadListings();
  }, [pagination.page, selectedCategory, search]);

  const loadCategories = async () => {
    try {
      const res = await apiFetch('/api/v1/marketplace/categories');
      if (res.ok) {
        const data = await res.json();
        setCategories(data);
      }
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadListings = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('page', pagination.page);
      params.append('per_page', pagination.per_page);
      
      if (search) params.append('q', search);
      if (selectedCategory) params.append('category', selectedCategory);

      const res = await apiFetch(`/api/v1/marketplace/blocks?${params}`);
      if (res.ok) {
        const data = await res.json();
        setListings(data.items || []);
        setPagination(prev => ({ ...prev, total: data.total }));
      }
    } catch (error) {
      console.error('Error loading listings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value) => {
    setSearch(value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleCategoryChange = (categorySlug) => {
    setSelectedCategory(categorySlug);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const categoryMenu = {
    items: [
      { key: null, label: 'All Categories' },
      ...categories.map(c => ({ key: c.slug, label: c.name }))
    ],
    onClick: ({ key }) => handleCategoryChange(key),
  };

  return (
    <div className="marketplace-browse" style={{ padding: 24 }}>
      <div className="mb-4">
        <Title level={2}>
          <ShopOutlined /> Marketplace
        </Title>
        <Text type="secondary">
          Discover and install blocks to extend your ERP
        </Text>
      </div>

      {/* Search and Filter Bar */}
      <div className="mb-4">
        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Input.Search
              placeholder="Search blocks..."
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              onSearch={handleSearch}
            />
          </Col>
          <Col xs={24} md={6}>
            <Dropdown menu={categoryMenu} trigger={['click']}>
              <Button size="large" block icon={<FilterOutlined />}>
                {selectedCategory 
                  ? categories.find(c => c.slug === selectedCategory)?.name 
                  : 'All Categories'}
              </Button>
            </Dropdown>
          </Col>
        </Row>
      </div>

      {/* Category Tags */}
      <div className="mb-4">
        <Space wrap>
          <Tag 
            color={!selectedCategory ? 'blue' : 'default'} 
            style={{ cursor: 'pointer' }}
            onClick={() => handleCategoryChange(null)}
          >
            All
          </Tag>
          {categories.map(cat => (
            <Tag 
              key={cat.slug}
              color={selectedCategory === cat.slug ? 'blue' : 'default'} 
              style={{ cursor: 'pointer' }}
              onClick={() => handleCategoryChange(cat.slug)}
            >
              {cat.name} ({cat.block_count || 0})
            </Tag>
          ))}
        </Space>
      </div>

      {/* Results */}
      {loading ? (
        <div className="text-center p-5"><Spin size="large" /></div>
      ) : listings.length === 0 ? (
        <Empty description="No blocks found" />
      ) : (
        <>
          <Row gutter={[16, 16]}>
            {listings.map(listing => (
              <Col xs={24} sm={12} lg={8} xl={6} key={listing.id}>
                <Card
                  hoverable
                  cover={
                    listing.thumbnail_url ? (
                      <img 
                        alt={listing.title} 
                        src={listing.thumbnail_url} 
                        style={{ height: 150, objectFit: 'cover' }}
                      />
                    ) : (
                      <div style={{ height: 150, background: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <ShopOutlined style={{ fontSize: 48, color: '#ccc' }} />
                      </div>
                    )
                  }
                  actions={[
                    <Button type="text" icon={<StarOutlined />}>
                      {listing.rating_avg?.toFixed(1) || '0.0'}
                    </Button>,
                    <Button type="primary" icon={<DownloadOutlined />}>
                      Install
                    </Button>,
                  ]}
                >
                  <Card.Meta
                    title={listing.title}
                    description={
                      <Space direction="vertical" size={0}>
                        <Paragraph ellipsis={{ rows: 2 }} style={{ margin: 0 }}>
                          {listing.description}
                        </Paragraph>
                        <Space>
                          <Text type="secondary">by {listing.author?.display_name || 'Unknown'}</Text>
                        </Space>
                        <Space>
                          {listing.price > 0 ? (
                            <Text strong>€{listing.price}</Text>
                          ) : (
                            <Tag color="green">Free</Tag>
                          )}
                          <Text type="secondary">|</Text>
                          <Text type="secondary">{listing.downloads} downloads</Text>
                        </Space>
                      </Space>
                    }
                  />
                </Card>
              </Col>
            ))}
          </Row>
          
          <div className="text-center mt-4">
            <Pagination
              current={pagination.page}
              pageSize={pagination.per_page}
              total={pagination.total}
              onChange={(page) => setPagination(prev => ({ ...prev, page }))}
              showSizeChanger={false}
            />
          </div>
        </>
      )}
    </div>
  );
}

export default MarketplaceBrowse;
