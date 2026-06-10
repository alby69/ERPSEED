import React, { useState, useEffect, useCallback } from 'react';
import { Card, Form, Select, InputNumber, Button, Typography, Row, Col, Spin, Alert, Space, Tag, Divider, message, Descriptions } from 'antd';
import { SwapOutlined, EnvironmentOutlined, CarOutlined, AimOutlined, CalculatorOutlined } from '@ant-design/icons';
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from 'react-leaflet';
import Layout from '../components/Layout'; // Importa Layout
import L from 'leaflet';
import { apiFetch } from '@/utils';
import { useTheme } from '@/context';
import 'leaflet/dist/leaflet.css';

// delete L.Icon.Default.prototype._getIconUrl; // Non è più necessario con le ultime versioni di React-Leaflet
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const { Title, Text } = Typography;

const START_COLOR = '#52c41a';
const END_COLOR = '#ff4d4f';

function createColoredIcon(color) {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background:${color};width:24px;height:24px;border-radius:50%;border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:bold;">●</div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
}

function FitBounds({ points }) {
  const map = useMap();
  useEffect(() => {
    if (points.length >= 2) {
      const bounds = L.latLngBounds(points.map(p => [p[1], p[0]]));
      map.fitBounds(bounds, { padding: [50, 50] });
    } else if (points.length === 1) {
      map.setView([points[0][1], points[0][0]], 13);
    }
  }, [points, map]);
  return null;
}

function formatDuration(seconds) {
  if (!seconds && seconds !== 0) return '-';
  const h = Math.floor(seconds / 3600);
  const m = Math.round((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}min`;
  return `${m} min`;
}

function formatDistance(meters) {
  if (!meters && meters !== 0) return '-';
  const km = meters / 1000;
  return km >= 1 ? `${km.toFixed(1)} km` : `${Math.round(meters)} m`;
}

function DistanceCalculator() {
  const { themeConfig } = useTheme();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [searchingStart, setSearchingStart] = useState(false);
  const [searchingEnd, setSearchingEnd] = useState(false);
  const [addresses, setAddresses] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [startCoords, setStartCoords] = useState(null);
  const [endCoords, setEndCoords] = useState(null);
  const [startName, setStartName] = useState('');
  const [endName, setEndName] = useState('');

  useEffect(() => {
    loadAddresses();
  }, []);

  const loadAddresses = async () => {
    try {
      const resp = await apiFetch('/api/v1/indirizzi?per_page=500');
      const data = await resp.json();
      const items = data.items || data.data || data || [];
      setAddresses(items);
    } catch {
      console.warn('Could not load addresses');
    }
  };

  const handleCalculate = async (values) => {
    setLoading(true);
    setError(null);
    setResult(null);

    let startLng = values.start_lng, startLat = values.start_lat;
    let endLng = values.end_lng, endLat = values.end_lat;

    if (values.start_address_id) {
      const addr = addresses.find(a => a.id === values.start_address_id);
      if (addr) {
        startLng = addr.longitudine;
        startLat = addr.latitudine;
      }
    }
    if (values.end_address_id) {
      const addr = addresses.find(a => a.id === values.end_address_id);
      if (addr) {
        endLng = addr.longitudine;
        endLat = addr.latitudine;
      }
    }

    if (!startLng || !startLat || !endLng || !endLat) {
      setError('Seleziona indirizzi con coordinate valide o inserisci coordinate manualmente');
      setLoading(false);
      return;
    }

    setStartCoords([startLng, startLat]);
    setEndCoords([endLng, endLat]);
    const startAddr = values.start_address_id ? addresses.find(a => a.id === values.start_address_id) : null;
    const endAddr = values.end_address_id ? addresses.find(a => a.id === values.end_address_id) : null;
    setStartName(startAddr ? `${startAddr['città'] || ''}${startAddr.provincia ? ` (${startAddr.provincia})` : ''}` : (startLat && startLng ? 'Coordinate manuali' : ''));
    setEndName(endAddr ? `${endAddr['città'] || ''}${endAddr.provincia ? ` (${endAddr.provincia})` : ''}` : (endLat && endLng ? 'Coordinate manuali' : ''));

    try {
      const resp = await apiFetch('/api/v1/logistics/directions', {
        method: 'POST',
        body: JSON.stringify({
          start: [startLng, startLat],
          end: [endLng, endLat],
          profile: values.profile || 'driving-car',
        }),
      });
      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.message || 'Errore nel calcolo del percorso');
      }
      const data = await resp.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSwap = () => {
    const vals = form.getFieldsValue();
    form.setFieldsValue({
      start_address_id: vals.end_address_id,
      end_address_id: vals.start_address_id,
      start_lat: vals.end_lat,
      start_lng: vals.end_lng,
      end_lat: vals.start_lat,
      end_lng: vals.start_lng,
    });
    setStartCoords(null);
    setEndCoords(null);
    setResult(null);
    setError(null);
  };

  const coordsArray = [];
  if (startCoords) coordsArray.push(startCoords);
  if (endCoords) coordsArray.push(endCoords);

  return (
    <Layout>
      <div style={{ padding: 24, background: themeConfig.mode === 'dark' ? '#141414' : '#f5f5f5', minHeight: '100vh' }}>
        <Title level={3} style={{ marginBottom: 8 }}>Logistica (
          <CalculatorOutlined /> Calcolo Distanze
        </Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
          Calcola percorsi e distanze tra due punti geografici
        </Text>

        <Row gutter={24}>
          <Col xs={24} lg={8}>
            <Card title="Percorso" size="small" style={{ marginBottom: 16 }}>
              <Form form={form} layout="vertical" onFinish={handleCalculate} initialValues={{ profile: 'driving-car' }}>
                <Form.Item label="Partenza — Indirizzo" name="start_address_id">
                  <Select
                    showSearch
                    allowClear
                    placeholder="Cerca indirizzo..."
                    optionFilterProp="label"
                    loading={searchingStart}
                    options={addresses
                      .filter(a => a.latitudine && a.longitudine)
                      .map(a => ({
                        label: `${a.denominazione || ''}, ${a['città'] || ''}${a['città'] ? ', ' : ''}${a.provincia || ''}`,
                        value: a.id,
                      }))}
                  />
                </Form.Item>

                <Text type="secondary" style={{ fontSize: 12 }}>— oppure coordinate manuali —</Text>
                <Row gutter={8}>
                  <Col span={12}>
                    <Form.Item name="start_lat" label="Lat." size="small">
                      <InputNumber step={0.0001} style={{ width: '100%' }} size="small" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item name="start_lng" label="Lng." size="small">
                      <InputNumber step={0.0001} style={{ width: '100%' }} size="small" />
                    </Form.Item>
                  </Col>
                </Row>

                <Divider style={{ margin: '8px 0' }} />
                <div style={{ textAlign: 'center', marginBottom: 8 }}><Button icon={<SwapOutlined />} onClick={handleSwap} size="small">Scambia A↔B</Button></div>
                <Divider style={{ margin: '8px 0' }} />

                <Form.Item label="Arrivo — Indirizzo" name="end_address_id">
                  <Select
                    showSearch
                    allowClear
                    placeholder="Cerca indirizzo..."
                    optionFilterProp="label"
                    loading={searchingEnd}
                    options={addresses
                      .filter(a => a.latitudine && a.longitudine)
                      .map(a => ({
                        label: `${a.denominazione || ''}, ${a['città'] || ''}${a['città'] ? ', ' : ''}${a.provincia || ''}`,
                        value: a.id,
                      }))}
                  />
                </Form.Item>
                <Text type="secondary" style={{ fontSize: 12 }}>— oppure coordinate manuali —</Text>
                <Row gutter={8}>
                  <Col span={12}><Form.Item name="end_lat" label="Lat." size="small"><InputNumber step={0.0001} style={{ width: '100%' }} size="small" /></Form.Item></Col>
                  <Col span={12}><Form.Item name="end_lng" label="Lng." size="small"><InputNumber step={0.0001} style={{ width: '100%' }} size="small" /></Form.Item></Col>
                </Row>
                <Form.Item name="profile" label="Mezzo">
                  <Select>
                    <Select.Option value="driving-car">Auto</Select.Option>
                    <Select.Option value="driving-hgv">Camion</Select.Option>
                    <Select.Option value="cycling-regular">Bici</Select.Option>
                    <Select.Option value="foot-walking">Pedoni</Select.Option>
                  </Select>
                </Form.Item>
                <Button type="primary" htmlType="submit" loading={loading} block icon={<CarOutlined />}>Calcola Percorso</Button>
              </Form>
            </Card>
            {error && <Alert message={error} type="error" showIcon closable style={{ marginBottom: 16 }} onClose={() => setError(null)} />}
            {result && (
              <Card title="Risultati" size="small">
                <Descriptions column={1} size="small">
                  {(startName || endName) && (<><Descriptions.Item label="Partenza"><Text>{startName || '-'}</Text></Descriptions.Item><Descriptions.Item label="Arrivo"><Text>{endName || '-'}</Text></Descriptions.Item></>)}
                  <Descriptions.Item label="Distanza"><Text strong style={{ fontSize: 18, color: themeConfig.primaryColor }}>{formatDistance(result.distance)}</Text></Descriptions.Item>
                  <Descriptions.Item label="Durata"><Text strong>{formatDuration(result.duration)}</Text></Descriptions.Item>
                  <Descriptions.Item label="Fonte"><Tag>{result.provider === 'haversine' ? 'Stima lineare' : 'OpenRouteService'}</Tag></Descriptions.Item>
                </Descriptions>
                {result.provider === 'haversine' && <Alert message="Stima lineare" description="Il risultato è una distanza in linea d'aria. Per percorsi reali, imposta OPENROUTESERVICE_API_KEY." type="warning" showIcon style={{ marginTop: 8, fontSize: 12 }} />}
              </Card>
            )}
          </Col>
          <Col xs={24} lg={16}>
            <Card bodyStyle={{ padding: 0 }} style={{ height: 600 }}>
              {coordsArray.length > 0 ? (
                <MapContainer center={[41.9, 12.5]} zoom={6} style={{ height: '100%', width: '100%' }}>
                  <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                  <FitBounds points={coordsArray} />
                  {startCoords && <Marker position={[startCoords[1], startCoords[0]]} icon={createColoredIcon(START_COLOR)}><Popup>Partenza</Popup></Marker>}
                  {endCoords && <Marker position={[endCoords[1], endCoords[0]]} icon={createColoredIcon(END_COLOR)}><Popup>Arrivo</Popup></Marker>}
                  {startCoords && endCoords && (
                    <Polyline positions={[[startCoords[1], startCoords[0]], [endCoords[1], endCoords[0]]]} color={themeConfig.primaryColor || '#1677ff'} weight={3} dashArray={result?.provider === 'haversine' ? '10, 10' : null} />
                  )}
                </MapContainer>
              ) : (
                <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: themeConfig.mode === 'dark' ? '#1f1f1f' : '#fafafa' }}>
                  <Space direction="vertical" align="center"><AimOutlined style={{ fontSize: 48, color: themeConfig.mode === 'dark' ? 'rgba(255,255,255,0.15)' : '#d9d9d9' }} /><Text type="secondary">Seleziona partenza e arrivo, poi calcola il percorso</Text></Space>
                </div>
              )}
            </Card>
          </Col>
        </Row>
      </div>
    </Layout>
  );
}

export default DistanceCalculator;
