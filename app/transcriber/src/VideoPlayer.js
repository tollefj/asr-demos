import { Player } from 'video-react';

export default props => {
  return (
    <Player>
      {/* source from public folder mp4 */}
      <source src="public/Debatten12okt.mp4" />
    </Player>
  );
};