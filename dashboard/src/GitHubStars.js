import React from 'react';
import {
  Subscription,
} from 'react-apollo';
import { Chart } from 'react-google-charts';
import gql from 'graphql-tag';

const GITHUB_STARS = gql`
subscription {
  github_stars_by_day_agg(order_by: {date: asc}) {
    stars
    date
  }
}
`;

const renderChart = (data) => {
  const d = [
    [
      { type: 'date', label: 'Day' },
      'stars'
    ]
  ];
  for (var r of data.github_stars_by_day_agg) {
    d.push([new Date(r.date), parseInt(r.stars, 10)]);
  }

  return (
    <Chart className="renderChart"
      height={'600px'}
      margin={'20px auto'}
      chartType="LineChart"
      loader={<div>Loading Chart</div>}
      data={d}
      options={{
        hAxis: {
          title: 'Date 🗓',
        },
        vAxis: {
          title: 'Stars ★',
        },
        series: {
          1: { curveType: 'function' },
        },
        height: '100%',
          title: 'Cumulative stars over days 🚀',
        legend: { position: 'none' },
        animation:{
          duration: 1000,
          easing: 'out',
          startup: true,
        },
      }}
    />
  )
};

export const GitHubStars = () => (
  <Subscription subscription={GITHUB_STARS}>
    {({ loading, error, data }) => {
      if (loading) return <p>Loading...</p>;
      if (error) return <p>Error :</p>;
      return (
        <div>
          <div className="chart">
            {renderChart(data)}
          </div>
        </div>
      );
    }}
  </Subscription>
)